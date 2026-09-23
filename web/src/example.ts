import type { ForecastRequest, RunResult } from './types';

// UI fixture only. Never used as a fallback for API failure.
export function exampleResult(request: ForecastRequest): RunResult {
  const runId = 'synthetic-ui-example';
  return {
    request, mode: 'example', warnings: ['Синтетические значения для проверки интерфейса. Не являются прогнозом ВЭС.'],
    status: { run_id: runId, state: 'example', model_version: 'synthetic-fixture', mode: 'example' },
    events: [],
    rows: request.turbine_ids.flatMap((turbine, index) => Array.from({ length: request.horizon_hours }, (_, i) => ({
      run_id: runId, turbine_id: turbine, issue_time: request.issue_time,
      valid_time: new Date(Date.parse(request.issue_time) + (i + 1) * 3600000).toISOString(),
      lead_hours: i + 1, y_pred: Number(Math.max(0, Math.min(1, 0.43 + 0.21 * Math.sin(i / 5) + 0.07 * Math.cos(i / 2) - index * 0.035)).toFixed(4)),
      unit: 'normalized_power', model_version: 'synthetic-fixture', weather_reference: 'SYNTHETIC_NO_WEATHER', fallback_status: null,
    }))),
  };
}
