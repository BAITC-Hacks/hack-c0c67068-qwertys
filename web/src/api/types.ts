// UI-side view of the backend contract (coordination/CONTRACTS.md + C4 proposed routes).
// All timestamps are ISO 8601 strings WITH offset. Power is normalized (0..1), never MW/MWh.

export type RunState = 'queued' | 'running' | 'succeeded' | 'degraded' | 'failed' | 'not_ready'
export type RunMode = 'live' | 'saved' | 'synthetic'
export type LlmMode = 'llm' | 'deterministic'
export type FallbackStatus = 'none' | 'power_curve' | 'previous_run'

export interface WeatherRef {
  provider: string // "open-meteo"
  model: string // "ecmwf_ifs"
  run_init: string // model initialisation time (UTC)
  available_at: string // conservative availability time used by the gate
  available_at_rule: string // e.g. "run_init + 6h"
  source_url?: string
  response_sha256?: string
}

export interface RunSummary {
  run_id: string
  issue_time: string
  turbine_ids: string[]
  horizon_hours: 24 | 48
  state: RunState
  mode: RunMode
  llm_mode: LlmMode
  started_at: string
  updated_at: string
  model_version: string
  weather: WeatherRef | null
  supersedes?: string | null // previous run_id of the same issue (recompute)
  warnings: string[]
  safe_errors: string[]
}

export interface ForecastRow {
  run_id: string
  turbine_id: string
  issue_time: string
  valid_time: string
  lead_hours: number
  y_pred: number
  y_p10?: number | null
  y_p90?: number | null
  unit: string // "normalized_power"
  model_version: string
  weather_run_init?: string | null
  fallback_status: FallbackStatus
}

export interface AgentEvent {
  run_id: string
  seq: number
  ts: string
  tool_name: string
  state_transition: string // e.g. "FETCH->VALIDATE"
  safe_input_summary: string
  result_summary: string
  status: 'ok' | 'retry' | 'error' | 'skipped' | 'decision'
  retry_count: number
  duration_ms?: number | null
}

export interface EvaluationRow {
  model: string
  turbine_id: string
  lead_bucket: string // "1-24" | "25-48"
  mae: number
  rmse: number
  n: number
}

export interface Evaluation {
  source: 'history_backtest'
  period_start: string
  period_end: string
  protocol: string
  rows: EvaluationRow[]
}

export interface Health {
  status: 'ok' | 'not_ready' | 'error'
  version?: string
  data_ready?: boolean
  message?: string
}

export interface RunRequest {
  issue_time: string
  turbine_ids: string[]
  horizon_hours: 24 | 48
  force_recompute?: boolean
}
