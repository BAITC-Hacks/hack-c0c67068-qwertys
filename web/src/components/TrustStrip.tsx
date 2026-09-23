import type { ForecastMetadata, ForecastRow, RunStatus } from '../api/types'
import { fmtIso, type DisplayTz } from '../lib/time'

interface Props {
  metadata: ForecastMetadata | null
  status: RunStatus | null
  rows: ForecastRow[]
  horizon: number
  turbines: number
  tz: DisplayTz
  synthetic: boolean
}

const MODE_LABEL: Record<string, string> = {
  live: 'live — агент с LLM',
  cached: 'cached — сохранённые входы',
  deterministic: 'deterministic — без LLM',
}

/** Key limitations visible BEFORE the chart; full provenance on demand. */
export function TrustStrip({ metadata: m, status, rows, horizon, turbines, tz, synthetic }: Props) {
  if (synthetic) return null
  const filled = rows.filter((r) => r.y_pred != null).length
  const expected = horizon * turbines
  const inferred = [m?.provenance_status, m?.timezone_status].some((s) => s && s !== 'confirmed')
  return (
    <details className="trust">
      <summary>
        <span className={`tchip ${status?.mode === 'live' ? 'ok' : ''}`}>режим: {status?.mode ? MODE_LABEL[status.mode] ?? status.mode : 'неизвестно'}</span>
        <span className="tchip">
          погода: {m?.weather_model ?? '?'} · прогон {fmtIso(m?.weather_run_time, tz) ?? 'неизвестно'}
        </span>
        <span className={`tchip ${filled === expected ? 'ok' : 'warn'}`}>
          покрытие {filled}/{expected} ч
        </span>
        {inferred && <span className="tchip warn">⚠ доступность погоды и время SCADA — допущения</span>}
        {!!status?.warnings?.length && <span className="tchip warn">предупреждений: {status.warnings.length}</span>}
        <span className="tmore">подробнее</span>
      </summary>
      <div className="trust-body">
        <p>
          Прогноз построен только на прогнозе погоды, который считается доступным к моменту выпуска
          {m?.availability_basis ? ` (правило: ${m.availability_basis})` : ''}. Статус происхождения: {m?.provenance_status ?? 'неизвестно'}; время SCADA:{' '}
          {m?.scada_timezone ?? 'неизвестно'} ({m?.timezone_status ?? '?'}).
        </p>
        {!!status?.warnings?.length && (
          <ul>
            {status.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        )}
      </div>
    </details>
  )
}
