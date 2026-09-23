// UI view of coordination/API_CONTRACT_V1.md (C3). snake_case JSON, RFC3339 timestamps
// with offset (responses in UTC "Z"). Power is `normalized_power`, never MW/MWh.

export type TurbineId = 'turbine_1' | 'turbine_2'
export type RunStatusValue = 'queued' | 'running' | 'completed' | 'failed'
export type Stage = 'weather' | 'prepare' | 'forecast' | 'validate' | 'export' | null
export type RunMode = 'live' | 'cached' | 'deterministic'

export interface ApiError {
  code: string
  message: string
  retryable: boolean
}

export interface Health {
  status: string
  forecast_ready: boolean
}

export interface RunRequest {
  issue_time: string
  turbine_ids: TurbineId[]
  horizon_hours: 24 | 48
}

export interface RunStatus {
  run_id: string
  status: RunStatusValue
  stage: Stage
  mode: RunMode
  forecast_available: boolean
  warnings: string[]
  error: ApiError | null
  // Not in V1 but tolerated if the backend adds them:
  issue_time?: string
  horizon_hours?: 24 | 48
  turbine_ids?: TurbineId[]
}

export interface ForecastRow {
  turbine_id: TurbineId
  issue_time: string
  valid_time: string
  lead_hours: number
  y_pred: number
}

export interface ForecastMetadata {
  model_version: string | null
  input_version: string | null
  weather_provider: string | null
  weather_model: string | null
  weather_run_time: string | null
  weather_available_at: string | null
  availability_basis: string | null
  scada_timezone: string | null
  timezone_status: string | null
  provenance_status: string | null
}

export interface ForecastResponse {
  run_id: string
  unit: string
  rows: ForecastRow[]
  metadata: ForecastMetadata
}

export interface AgentEvent {
  seq: number
  timestamp: string
  tool: string
  state: string
  summary: string
}

export interface EventsResponse {
  run_id: string
  events: AgentEvent[]
}

/** Optional (not in V1): history backtest table. UI shows "недоступно" when absent. */
export interface EvaluationRow {
  model: string
  turbine_id: string
  lead_bucket: string
  mae: number
  rmse: number
  n: number
}
export interface Evaluation {
  period_start: string
  period_end: string
  protocol: string
  rows: EvaluationRow[]
}

/** A run as the UI remembers it (params are what the UI sent). */
export interface RunRecord {
  run_id: string
  request: RunRequest
  created_at: string
  synthetic: boolean
}
