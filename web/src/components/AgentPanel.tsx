import type { AgentEvent, RunStatus, Stage } from '../api/types'
import { fmtIso, type DisplayTz } from '../lib/time'

const STAGES: { key: Exclude<Stage, null>; label: string }[] = [
  { key: 'weather', label: 'Погода' },
  { key: 'prepare', label: 'Данные' },
  { key: 'forecast', label: 'Модель' },
  { key: 'validate', label: 'Анализ' },
  { key: 'export', label: 'Экспорт' },
]
const STAGE_LABEL = Object.fromEntries(STAGES.map((s) => [s.key, s.label])) as Record<string, string>

function stageState(i: number, status: RunStatus | null): 'done' | 'active' | 'failed' | 'pending' {
  if (!status) return 'pending'
  if (status.status === 'completed') return 'done'
  const cur = STAGES.findIndex((s) => s.key === status.stage)
  if (status.status === 'failed') return i < cur ? 'done' : i === cur ? 'failed' : 'pending'
  if (cur < 0) return 'pending'
  return i < cur ? 'done' : i === cur ? 'active' : 'pending'
}
const ICON = { done: '✓', active: '●', failed: '✕', pending: '○' }

const isError = (e: AgentEvent) => /error|fail|exception|unavailable|reject/i.test(`${e.state} ${e.tool}`)
const isRetry = (e: AgentEvent) => /retry|fallback|degrad/i.test(`${e.state} ${e.tool}`)

interface Props {
  status: RunStatus | null
  events: AgentEvent[]
  tz: DisplayTz
  synthetic: boolean
}

export function AgentPanel({ status, events, tz, synthetic }: Props) {
  const running = status?.status === 'queued' || status?.status === 'running'
  const t0 = events.length ? Date.parse(events[0].timestamp) : null
  return (
    <section className="card" aria-labelledby="agent-h">
      <h2 id="agent-h">
        Ход агента
        <small>{synthetic ? 'синтетика — инструменты не вызывались' : status ? `run ${status.run_id}` : 'нет запуска'}</small>
      </h2>
      <div className="pipeline" role="list" aria-label="Этапы агентного цикла">
        {STAGES.map((s, i) => {
          const st = synthetic ? 'pending' : stageState(i, status)
          const n = events.filter((e) => e.stage === s.key).length
          return (
            <div key={s.key} role="listitem" className={`stage ${st}`} aria-label={`${s.label}: ${st}, событий ${n}`}>
              <b aria-hidden>{ICON[st]}</b>
              {s.label}
              {n > 0 && <i className="stage-n">{n}</i>}
            </div>
          )
        })}
      </div>
      {status?.status === 'failed' && status.error && (
        <p className="agent-error" role="alert">
          ✕ {status.error.code}: {status.error.message}
          {status.error.retryable ? ' · можно повторить' : ''}
        </p>
      )}
      {events.length === 0 ? (
        <p className="unknown" style={{ marginTop: 10 }}>
          {running ? 'Ожидание первых событий от агента…' : 'Журнал пуст — события появятся после реального запуска.'}
        </p>
      ) : (
        <ol className="timeline" aria-label="Журнал инструментов" aria-live="polite">
          {events.map((e) => {
            const kind = isError(e) ? 'err' : isRetry(e) ? 'retry' : ''
            const dt = t0 != null ? ((Date.parse(e.timestamp) - t0) / 1000).toFixed(1) : null
            return (
              <li key={e.seq} className={kind}>
                <span className="seq">{e.seq}</span>
                <details>
                  <summary>
                    <span className="tool">{e.tool}</span>
                    <span className="state">{e.state}</span>
                    {dt != null && <time dateTime={e.timestamp}>+{dt} с</time>}
                    <div className="sum">{e.summary}</div>
                  </summary>
                  <dl className="kv ev">
                    <dt>этап</dt>
                    <dd>{e.stage ? STAGE_LABEL[e.stage] ?? e.stage : '—'}</dd>
                    <dt>время</dt>
                    <dd>{fmtIso(e.timestamp, tz)}</dd>
                    <dt>шаг</dt>
                    <dd>
                      #{e.seq} · {e.tool} → {e.state}
                    </dd>
                  </dl>
                </details>
              </li>
            )
          })}
        </ol>
      )}
    </section>
  )
}
