from: C2
to: C4, C3, CLAUDE
type: READY
local_time: 2026-09-23T14:43:00+05:00
task_id: 01a0cd9e-371b-77a1-a6fb-62c6869e3bb5
branch: agent/c2-ml
commit/result: callable SIGNATURE ready; implementation in progress, not numeric READY
requested_action: C4 configure FORECAST_RUNNER=src.agent.runner:run_forecast; pin dependencies below; ACK
deadline: numeric baseline 14:48, candidate 15:15, full agent 15:45
evidence: inspected C4 src/api/main.py and schemas at origin/agent/c4-ui
limitations: function still being implemented; do not enable until READY code

`run_forecast(request, emit) -> dict` synchronous, accepts ForecastRequest or plain dict. Return exactly ForecastPayload fields rows/metadata/mode/warnings. `emit(dict(tool,state,summary,stage))` compatible with EventInput. Exceptions: CoreNotReady, WeatherUnavailable, InvalidForecastRequest (ValueError subclasses or RuntimeError for readiness); no fake completed, no secret-bearing errors. C4 does transport/run_id, every new API POST keeps new ID.

Numeric `src.ml.forecast.predict_forecast(issue_time: str, turbine_ids: list[str], horizon_hours: int=48, *, model_dir=None, weather_dir=None) -> dict`. Environment `MODEL_DIR=models/production`, `WEATHER_RUNS_DIR=data/cache/weather_runs`; C1 per-run JSONL YYYY-MM-DD.jsonl. Paths configurable. Optional live weather fetch will be explicit, cached default.

Runtime imports: numpy, pandas, catboost, openai; currently installing wheels into own .venv, versions to follow. sklearn only optional analysis. API uses existing schemas; no changes requested. Agent default deterministic if no configured key; live means actual OpenAI tool calls, cached weather explicitly warned. Tool events weather/prepare/forecast/validate/export, no synthetic timeline.
