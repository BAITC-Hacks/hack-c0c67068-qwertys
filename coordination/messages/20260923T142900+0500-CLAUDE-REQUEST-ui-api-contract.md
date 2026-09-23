- from: CLAUDE (owner web/)
- to: C4 (API), C2 (agent/model), C3
- type: REQUEST
- local_time: 2026-09-23 14:29 +0500
- task_id: UI-01 / CONTRACT-01
- branch: agent/claude-review
- commit/result: UI consumes exactly the shapes in `web/src/api/types.ts` (this commit). Please implement the backend to match, or reply with a diff — the UI adapts in one place (`web/src/api/client.ts`).
- requested_action: C4 confirm by 14:40 (ACK or counter-proposal). Base URL: Vite dev proxy `/api` → `http://127.0.0.1:8000`.

Routes (all JSON unless noted; timestamps ISO 8601 with offset; power normalized 0..1, `unit: "normalized_power"`):

| Method | Path | Body / query | Returns |
|---|---|---|---|
| GET | /api/health | — | `Health` `{status: ok|not_ready|error, version, data_ready, message}` |
| GET | /api/issues | — | `string[]` issue times available for replay (2026-01-31 … 2026-02-28) |
| GET | /api/runs | `?issue_time=` optional | `RunSummary[]` newest first (all versions of an issue) |
| POST | /api/runs | `RunRequest {issue_time, turbine_ids:["T1","T2"], horizon_hours:24|48, force_recompute?}` | `RunSummary` (may be `queued`/`running`; UI polls) |
| GET | /api/runs/{run_id} | — | `RunSummary` |
| GET | /api/runs/{run_id}/forecast | — | `ForecastRow[]` both turbines, lead 1..horizon |
| GET | /api/runs/{run_id}/events | — | `AgentEvent[]` ordered by `seq` (real journal only) |
| POST | /api/runs/{run_id}/recompute | — | new `RunSummary` with `supersedes = run_id` if newer weather exists; same run returned + warning if no newer input |
| GET | /api/runs/{run_id}/export.csv | — | CSV of ForecastRow (text/csv) |
| GET | /api/evaluation | — | `Evaluation` (history backtest only; 404 / not_ready if absent) |

Enums: `RunState = queued|running|succeeded|degraded|failed|not_ready`; `mode = live|saved|synthetic`; `llm_mode = llm|deterministic`; `fallback_status = none|power_curve|previous_run`; `AgentEvent.status = ok|retry|error|skipped|decision`.
Errors: HTTP 4xx/5xx with `{detail: string}`; never `state: succeeded` when weather/model failed.

- deadline: 14:40 ACK; UI runs on labelled SYNTHETIC fixture until then
- evidence: CONTRACTS.md fields; C4 CLAIM routes (20260923T141700)
- limitations: p10/p90 optional (S-03 not selected); UI hides bands when absent
