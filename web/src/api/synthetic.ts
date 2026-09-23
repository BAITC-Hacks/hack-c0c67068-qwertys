// SYNTHETIC fixture — used only when the user explicitly switches to the demo mode
// while the backend is not ready. Deterministic shapes, NOT a forecast, NOT weather.
import type { AgentEvent, ForecastResponse, RunRequest, TurbineId } from './types'

export const SYNTHETIC_TAG = 'СИНТЕТИКА — не прогноз'

function hash(s: string): number {
  let h = 2166136261
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619)
  return (h >>> 0) / 4294967295
}

export function syntheticForecast(runId: string, req: RunRequest): ForecastResponse {
  const issue = new Date(req.issue_time).getTime()
  const phase = hash(req.issue_time) * Math.PI * 2
  const rows = []
  for (const t of req.turbine_ids) {
    const k = t === 'turbine_1' ? 1 : 0.93
    for (let lead = 1; lead <= req.horizon_hours; lead++) {
      const base = 0.45 + 0.3 * Math.sin(lead / 7 + phase) + 0.12 * Math.sin(lead / 2.3 + phase * 2)
      rows.push({
        turbine_id: t as TurbineId,
        issue_time: new Date(issue).toISOString(),
        valid_time: new Date(issue + lead * 3600_000).toISOString(),
        lead_hours: lead,
        y_pred: Math.round(Math.min(1, Math.max(0, base * k)) * 1000) / 1000,
      })
    }
  }
  return {
    run_id: runId,
    unit: 'normalized_power',
    rows,
    metadata: {
      model_version: 'synthetic-fixture',
      input_version: null,
      weather_provider: null,
      weather_model: null,
      weather_run_time: null,
      weather_available_at: null,
      availability_basis: null,
      scada_timezone: null,
      timezone_status: null,
      provenance_status: 'synthetic',
    },
  }
}

export function syntheticEvents(): AgentEvent[] {
  const now = new Date().toISOString()
  return [
    { seq: 1, timestamp: now, tool: 'synthetic_fixture', state: 'DEMO', summary: 'Backend не подключён: показан синтетический пример формы данных. Инструменты агента не вызывались.' },
  ]
}
