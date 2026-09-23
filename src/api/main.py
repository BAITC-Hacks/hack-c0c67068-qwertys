"""Run: python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000.

Numerical adapter: sync runner(request: ForecastRequest, emit) -> ForecastPayload.
No synthetic fallback. Without an attached adapter POST returns 503.
"""
import csv
import importlib
import io
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path
from threading import BoundedSemaphore
from typing import Callable
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from src.api.store import RunStore, now
from src.contracts.schemas import ApiError, EventInput, EventResponse, ForecastPayload, ForecastRequest, ForecastResponse, RunStatus, check_payload

Runner = Callable[[ForecastRequest, Callable[[EventInput], None]], ForecastPayload]


def problem(status: int, code: str, message: str, retryable=False):
    raise HTTPException(status, detail=ApiError(code=code, message=message, retryable=retryable).model_dump())


def safe_summary(text: str) -> str:
    # Defense against accidental key inclusion in tool-generated text; do not log exception text.
    text = re.sub(r"(?i)(bearer\s+)[^\s,;]+", r"\1[REDACTED]", text)
    text = re.sub(r"\b(?:sk-|nvapi-)[a-zA-Z0-9_-]+", "[REDACTED]", text)
    text = re.sub(r"(?i)((?:api[_-]?key|token|password|secret)\s*[:=]\s*)[^\s,;&]+", r"\1[REDACTED]", text)
    return text


def configured_runner() -> Runner | None:
    target = os.getenv("FORECAST_RUNNER", "").strip()
    if not target:
        return None
    module, separator, function = target.partition(":")
    if not separator or not module.startswith("src."):
        raise ValueError("FORECAST_RUNNER must be src.module:function")
    runner = getattr(importlib.import_module(module), function)
    if not callable(runner):
        raise ValueError("FORECAST_RUNNER is not callable")
    return runner


def create_app(runner: Runner | None = None, store_path: Path | None = None, static_dir: Path | None = None, readiness: Callable | None = None) -> FastAPI:
    store = RunStore(store_path or Path(os.getenv("RUN_STORE_PATH", ".local/runs.sqlite3")))
    slots = BoundedSemaphore(4)

    @asynccontextmanager
    async def lifespan(application):
        store.recover_interrupted()
        application.state.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="forecast")
        yield
        application.state.executor.shutdown(wait=True, cancel_futures=False)

    app = FastAPI(title="QwertyS Wind Forecast", version="0.1.0", lifespan=lifespan)
    app.state.runner = runner
    app.state.store = store

    def forecast_ready():
        if app.state.runner is None:
            return False
        if readiness is None:
            return True
        try:
            return readiness().get("ready") is True
        except Exception:
            # Configuration errors must not expose filesystem paths or provider secrets.
            return False

    @app.exception_handler(HTTPException)
    async def http_error(_request, exc):
        error = exc.detail if isinstance(exc.detail, dict) else {"code": "request_error", "message": str(exc.detail), "retryable": False}
        return JSONResponse({"error": error}, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request, _exc):
        # Pydantic input/error contexts can echo secret payloads; keep public error bounded.
        return JSONResponse({"error": {"code": "invalid_request", "message": "Проверьте issue_time с часовым поясом, turbine_1/turbine_2 и горизонт 24/48", "retryable": False}}, status_code=422)

    def require_run(run_id):
        status = store.get(run_id)
        if status is None:
            problem(404, "unknown_run", "Запуск не найден")
        return status

    def require_forecast(run_id):
        require_run(run_id)
        forecast = store.forecast(run_id)
        if forecast is None:
            problem(409, "not_ready", "Результат расчёта ещё не готов", True)
        return forecast

    def execute(run_id, body):
        try:
            store.update(run_id, status="running")

            def emit(event):
                event = EventInput.model_validate(event)
                event.summary = safe_summary(event.summary)
                store.emit(run_id, event)

            emit(EventInput(tool="api", state="started", summary="Запрос передан вычислительному ядру"))
            payload = app.state.runner(body, emit)
            payload = ForecastPayload.model_validate(payload)
            warnings = check_payload(body, payload)
            warnings = [safe_summary(warning) for warning in warnings]
            emit(EventInput(tool="api.validate", state="ok", summary=f"Проверены время, идентификаторы и {len(payload.rows)} строк", stage="validate"))
            result = ForecastResponse(run_id=run_id, rows=payload.rows, metadata=payload.metadata)
            # Journal event describes real transport work, not a fabricated model/LLM call.
            emit(EventInput(tool="api.persist", state="ok", summary="Проверенный результат подготовлен к сохранению", stage="export"))
            store.finish(run_id, result, payload.mode, warnings)
        except Exception:
            store.update(run_id, status="failed", forecast_available=False, error=ApiError(code="calculation_failed", message="Расчёт или проверка результата завершились ошибкой. Проверьте входы и конфигурацию ядра.", retryable=True))
            store.emit(run_id, EventInput(tool="api", state="error", summary="Численный результат не опубликован: вычисление или проверка не прошли"))
        finally:
            slots.release()

    @app.get("/api/health")
    def health():
        return {"status": "ok", "forecast_ready": forecast_ready(), "version": app.version}

    @app.get("/api/evaluation")
    def evaluation(variant: str = "v1"):
        sources = {
            "v1": ("EVALUATION_PATH", "coordination/research/C2/evaluation-v1.json"),
            "v2": ("EVALUATION_V2_PATH", "coordination/research/C2/evaluation-v2-posttest.json"),
        }
        if variant not in sources:
            problem(422, "invalid_variant", "Допустимые варианты отчёта: v1 или v2")
        variable, default_path = sources[variant]
        path = Path(os.getenv(variable, default_path))
        if not path.is_file():
            problem(404, "not_found", "Отчёт исторической проверки ещё не опубликован")
        try:
            report = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(report, dict):
                raise ValueError("Expected report object")
            return JSONResponse(report)
        except (OSError, ValueError, TypeError):
            problem(503, "evaluation_unavailable", "Не удалось прочитать отчёт исторической проверки", True)

    @app.post("/api/runs", response_model=RunStatus, status_code=202)
    def start_run(body: ForecastRequest):
        if not forecast_ready():
            problem(503, "not_ready", "Модель или необходимые входные данные ещё не готовы")
        if not slots.acquire(blocking=False):
            problem(503, "busy", "Очередь расчётов заполнена. Повторите позже.", True)
        run_id = uuid4().hex
        created = now()
        status = RunStatus(run_id=run_id, status="queued", issue_time=body.issue_time, turbine_ids=body.turbine_ids, horizon_hours=body.horizon_hours, started_at=created, updated_at=created)
        try:
            store.create(status)
            app.state.executor.submit(execute, run_id, body)
        except Exception:
            slots.release()
            if store.get(run_id):
                store.update(run_id, status="failed", error=ApiError(code="queue_failed", message="Не удалось поставить расчёт в очередь", retryable=True))
            problem(503, "queue_failed", "Не удалось поставить расчёт в очередь", True)
        return status

    @app.get("/api/runs", response_model=list[RunStatus])
    def list_runs():
        return store.list_runs()

    @app.get("/api/runs/{run_id}", response_model=RunStatus)
    def get_run(run_id: str):
        return require_run(run_id)

    @app.get("/api/runs/{run_id}/forecast", response_model=ForecastResponse)
    def get_forecast(run_id: str):
        return require_forecast(run_id)

    @app.get("/api/runs/{run_id}/events", response_model=EventResponse)
    def get_events(run_id: str):
        require_run(run_id)
        return EventResponse(run_id=run_id, events=store.events(run_id))

    @app.get("/api/runs/{run_id}/export.csv")
    def export_csv(run_id: str):
        forecast = require_forecast(run_id)
        stream = io.StringIO(newline="")
        fields = ["run_id", "turbine_id", "issue_time", "valid_time", "lead_hours", "y_pred", "unit", *type(forecast.metadata).model_fields.keys()]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        metadata = forecast.metadata.model_dump(mode="json")
        for row in forecast.rows:
            values = {"run_id": run_id, "unit": forecast.unit, **row.model_dump(mode="json"), **metadata}
            # Guard spreadsheet formulas only on strings; numerical predictions keep numeric type.
            values = {key: "'" + value if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")) else value for key, value in values.items()}
            writer.writerow(values)
        return Response("\ufeff" + stream.getvalue(), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="forecast-{run_id}.csv"'})

    # Unknown API routes stay JSON errors rather than falling through to index.html.
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    def unknown_api(path: str):
        problem(404, "unknown_endpoint", "Маршрут API не найден")

    build = static_dir or Path("web/dist")
    if build.is_dir():
        app.mount("/", StaticFiles(directory=build, html=True), name="web")
    return app


load_dotenv()
_runner = configured_runner()
_readiness = getattr(importlib.import_module(_runner.__module__), "readiness", None) if _runner else None
app = create_app(runner=_runner, readiness=_readiness)
