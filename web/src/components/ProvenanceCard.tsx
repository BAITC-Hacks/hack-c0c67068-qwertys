import type { ForecastMetadata, RunStatus } from '../api/types'
import { fmtIso, type DisplayTz } from '../lib/time'

interface Props {
  metadata: ForecastMetadata | null
  status: RunStatus | null
  issueTime: string | null
  tz: DisplayTz
}

const U = () => <span className="unknown">неизвестно</span>

export function ProvenanceCard({ metadata: m, status, issueTime, tz }: Props) {
  const gateOk =
    m?.weather_available_at && issueTime ? Date.parse(m.weather_available_at) <= Date.parse(issueTime) : null
  return (
    <section className="card" aria-labelledby="prov-h">
      <h2 id="prov-h">Происхождение прогноза</h2>
      <dl className="kv">
        <dt>Выпуск (issue)</dt>
        <dd>{fmtIso(issueTime, tz) ?? <U />}</dd>
        <dt>Погода</dt>
        <dd>{m?.weather_provider ? `${m.weather_provider} · ${m.weather_model ?? '?'}` : <U />}</dd>
        <dt>Прогон модели</dt>
        <dd>{fmtIso(m?.weather_run_time, tz) ?? <U />}</dd>
        <dt>Доступен с</dt>
        <dd>
          {fmtIso(m?.weather_available_at, tz) ?? <U />}
          {m?.availability_basis && <div className="unknown">{m.availability_basis}</div>}
        </dd>
        <dt>Проверка времени</dt>
        <dd>
          {gateOk == null ? <U /> : gateOk ? '✓ доступен до выпуска' : '✕ позже выпуска — утечка!'}
        </dd>
        <dt>Модель</dt>
        <dd>{m?.model_version ?? <U />}</dd>
        <dt>Входные данные</dt>
        <dd>{m?.input_version ?? <U />}</dd>
        <dt>Время SCADA</dt>
        <dd>{m?.scada_timezone ? `${m.scada_timezone} (${m.timezone_status ?? '?'})` : <U />}</dd>
        <dt>Статус происхождения</dt>
        <dd>{m?.provenance_status ?? <U />}</dd>
        <dt>Режим</dt>
        <dd>{status?.mode ?? <U />}</dd>
      </dl>
      {!!status?.warnings?.length && (
        <ul className="warn-list" aria-label="Предупреждения">
          {status.warnings.map((w, i) => (
            <li key={i}>⚠ {w}</li>
          ))}
        </ul>
      )}
    </section>
  )
}
