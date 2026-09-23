export type Horizon = 24 | 48;
export type Mode = 'api' | 'example';
export interface ForecastRequest {
  issue_time: string;
  turbine_ids: string[];
  horizon_hours: Horizon;
  input_version: string;
}
export interface ForecastRow {
  run_id: string;
  turbine_id: string;
  issue_time: string;
  valid_time: string;
  lead_hours: number;
  y_pred: number | null;
  unit: string;
  model_version: string;
  weather_reference: string;
  fallback_status: string | null;
}
export interface AgentEvent {
  tool_name: string;
  state_transition: string;
  safe_input_summary?: string;
  result_reference?: string;
  retry_count?: number;
  timestamp?: string;
}
export interface WeatherSource {
  provider?: string;
  model?: string;
  run_time?: string;
  available_at?: string;
  source_reference?: string;
}
export interface RunStatus {
  run_id: string;
  state: string;
  started_at?: string;
  updated_at?: string;
  safe_errors?: string[];
  input_version?: string;
  model_version?: string;
  mode?: string;
  weather?: WeatherSource;
}
export interface RunResult {
  status: RunStatus;
  request: ForecastRequest;
  rows: ForecastRow[];
  events: AgentEvent[];
  mode: Mode;
  warnings: string[];
}
