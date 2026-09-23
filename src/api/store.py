"""SQLite run journal. One server process, durable results, immutable run IDs."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from src.contracts.schemas import AgentEvent, ApiError, EventInput, ForecastResponse, RunStatus


def now():
    return datetime.now(timezone.utc)


class RunStore:
    def __init__(self, path: Path):
        self.path = path
        self.lock = RLock()
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, status TEXT NOT NULL, forecast TEXT)")
            conn.execute("CREATE TABLE IF NOT EXISTS events (run_id TEXT NOT NULL, seq INTEGER NOT NULL, event TEXT NOT NULL, PRIMARY KEY(run_id, seq))")

    @contextmanager
    def connection(self):
        with self.lock:
            conn = sqlite3.connect(self.path, timeout=10)
            try:
                with conn:
                    yield conn
            finally:
                conn.close()

    def create(self, status: RunStatus):
        with self.connection() as conn:
            conn.execute("INSERT INTO runs (id,status) VALUES (?,?)", (status.run_id, status.model_dump_json()))

    def get(self, run_id: str) -> RunStatus | None:
        with self.connection() as conn:
            row = conn.execute("SELECT status FROM runs WHERE id=?", (run_id,)).fetchone()
        return RunStatus.model_validate_json(row[0]) if row else None

    def update(self, run_id: str, **changes):
        with self.lock:
            status = self.get(run_id)
            if status is None:
                raise KeyError(run_id)
            values = status.model_dump()
            values.update(changes, updated_at=now())
            status = RunStatus.model_validate(values)
            with self.connection() as conn:
                conn.execute("UPDATE runs SET status=? WHERE id=?", (status.model_dump_json(), run_id))
            return status

    def finish(self, run_id: str, forecast: ForecastResponse, mode: str, warnings: list[str]):
        with self.lock:
            status = self.get(run_id)
            if status is None:
                raise KeyError(run_id)
            status = RunStatus.model_validate({**status.model_dump(), "status": "completed", "stage": "export", "mode": mode, "forecast_available": True, "warnings": warnings, "updated_at": now()})
            with self.connection() as conn:
                conn.execute("UPDATE runs SET status=?, forecast=? WHERE id=?", (status.model_dump_json(), forecast.model_dump_json(), run_id))

    def forecast(self, run_id: str) -> ForecastResponse | None:
        with self.connection() as conn:
            row = conn.execute("SELECT forecast FROM runs WHERE id=?", (run_id,)).fetchone()
        return ForecastResponse.model_validate_json(row[0]) if row and row[0] else None

    def emit(self, run_id: str, event: EventInput):
        with self.connection() as conn:
            seq = conn.execute("SELECT COALESCE(MAX(seq),0)+1 FROM events WHERE run_id=?", (run_id,)).fetchone()[0]
            record = AgentEvent(**event.model_dump(), seq=seq, timestamp=now())
            conn.execute("INSERT INTO events VALUES (?,?,?)", (run_id, seq, record.model_dump_json()))
        if event.stage:
            self.update(run_id, stage=event.stage)

    def events(self, run_id: str) -> list[AgentEvent]:
        with self.connection() as conn:
            rows = conn.execute("SELECT event FROM events WHERE run_id=? ORDER BY seq", (run_id,)).fetchall()
        return [AgentEvent.model_validate_json(row[0]) for row in rows]

    def list_runs(self, limit=100) -> list[RunStatus]:
        with self.connection() as conn:
            rows = conn.execute("SELECT status FROM runs ORDER BY rowid DESC LIMIT ?", (limit,)).fetchall()
        return [RunStatus.model_validate_json(row[0]) for row in rows]

    def recover_interrupted(self):
        # Startup recovery deliberately covers all runs, not just list-page size.
        with self.connection() as conn:
            rows = conn.execute("SELECT id,status FROM runs").fetchall()
            for run_id, data in rows:
                status = RunStatus.model_validate_json(data)
                if status.status in ("queued", "running"):
                    status.status = "failed"
                    status.error = ApiError(code="interrupted", message="Сервер перезапущен до завершения расчёта", retryable=True)
                    status.updated_at = now()
                    conn.execute("UPDATE runs SET status=? WHERE id=?", (status.model_dump_json(), run_id))
