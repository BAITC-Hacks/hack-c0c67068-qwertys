# C4 HTTP transport handoff

Implemented against `coordination/API_CONTRACT_V1.md`. This is transport and contract validation, not proof of model quality. No production synthetic forecasts and no fabricated agent events. A missing numerical adapter returns HTTP 503 `not_ready`.

## Reproduce

Python 3.12, one local server process. From repository root:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-lock.txt
.venv/Scripts/python.exe -m pytest tests/integration -q
.venv/Scripts/python.exe scripts/verify_data.py "PATH_TO_OFFICIAL_CSV_DIRECTORY"
.venv/Scripts/python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Health: `http://127.0.0.1:8000/api/health`; interactive schema: `/docs`; machine schema: `/openapi.json`. Start with **one worker**; SQLite recovery marks interrupted queued/running work failed on startup. Up to four queued/active requests, one numerical calculation at a time. Results and journal remain in `.local/runs.sqlite3` (ignored). If `web/dist` exists at startup it is served at `/`; otherwise run Claude's Vite UI separately with proxy `/api`.

Actual check 2026-09-23 ~14:35 UTC+5: 19 integration tests pass, `pip check` passes, both official CSV SHA-256 values match DATA_MANIFEST. Tests inject a **synthetic stub**, explicitly labelled `TEST-STUB`; they do not show that a real model or weather service works. Production has no route that silently falls back to that stub.

## C2 adapter

Set `FORECAST_RUNNER=src.agent.YOUR_MODULE:YOUR_FUNCTION` in local `.env` (no secrets in Git). Restart API after enabling or changing adapter. Actual callable:

```python
from src.contracts.schemas import ForecastRequest, ForecastPayload, EventInput

def run_forecast(request: ForecastRequest, emit) -> ForecastPayload:
    # Your actual tool execution, not a fixture:
    # emit(EventInput(tool="weather", state="started", summary="Safe summary", stage="weather"))
    # ... fetch weather, call model, validate ...
    # Return ForecastPayload(rows=[...], metadata={...}, mode="deterministic", warnings=[...])
    ...
```

Pydantic object **or matching dictionary** is accepted for result and events. `ForecastRequest.issue_time` is a timezone-aware UTC datetime. Turbines are `turbine_1`, `turbine_2`. Row fields: turbine_id, issue_time, valid_time, lead_hours (1..48), y_pred (finite number or null). Do not include run_id/unit in numerical rows; HTTP wrapper owns them. Power is not clipped by transport.

Metadata fields: model_version, input_version, weather_provider, weather_model, weather_run_time, weather_available_at, availability_basis, scada_timezone, timezone_status, provenance_status. All optional unknown values remain null. Current C1 policy is `inferred_run_plus_9h`/`unconfirmed` (replaces +6h); it is inferred, not observed historical publication. HTTP validation rejects future weather, wrong request identity, duplicate hours, wrong leads, nonfinite or wholly missing numeric output. Partial coverage remains visible as warnings, without filling zeros.

Mode: `live` / `cached` / `deterministic`. Let the actual execution choose it; cache/no-LLM must not be labelled live LLM. `emit` accepts tool, state, summary and optional stage (`weather`, `prepare`, `forecast`, `validate`, `export`). API assigns sequence and UTC timestamp. Safe summaries only: do not include keys, auth headers, provider responses or raw exception tracebacks.

Integration additions beyond V1: GET `/api/runs` lists latest 100 existing runs. No invented list of available issues; no unsupported evaluation. Recompute is another POST to `/api/runs`; previous result is immutable. Captured weather/model/input version must be returned by C2 to explain the difference between runs.

## Limits and next checks

- Runtime of a numerical function is governed by C2's network/model timeouts; the API cannot safely kill a Python training thread. Shutdown waits for active calculations.
- Local interface only; no authentication or public deployment is provided.
- Python lock currently covers HTTP transport/testing only. C2 must send actual numerical and LLM imports for the single shared manifest.
- Claude owns `web/`; original C4 UI handoff 3192215 used the earlier provisional schema and is not the final integrated frontend.
- Browser and full real-data run are still pending C2 callable + Claude frontend integration.
