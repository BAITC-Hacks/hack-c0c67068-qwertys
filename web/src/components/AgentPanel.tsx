import type { AgentEvent, RunStatus, Stage } from '../api/types'
import { fmtIso, type DisplayTz } from '../lib/time'

const STAGES: { key: Exclude<Stage, null>; label: string }[] = [
  { key: 'weather', label: 'Погода' },
  { key: 'prepare', label: 'Данные' },
  { key: 'forecast', label: 'Модель' },
  { key: 'validate', label: 'Анализ' },
  { key: 'export', label: 'Экспорт' },
]

function stageState(i: number, status: RunStatus | null): 'done' | 'active' | 'failed' | 'pending' {
  if (!status) return 'pending'
  if (status.status === 'completed') return 'done'
  const cur = STAGES.findIndex((s) => s.key === status.stage)
  if (status.status === 'failed') return i < cur ? 'done' : i === cur ? 'failed' : 'pending'
  if (cur < 0) return 'pending'
  return i < cur ? 'done' : i === cur ? 'active' : 'pending'
}
const ICON = { done: '✓', active: '●', failed: '✕', pending: '○' }

interface Props {
  status: RunStatus | null
  events: AgentEvent[]
  tz: DisplayTz
  synthetic: boolean
}

export function AgentPanel({ status, events, tz, synthetic }: Props) {
  return (
    <section className="card" aria-labelledby="agent-h">
      <h2 id="agent-h">
        Ход агента
        <small>{synthetic ? 'синтетика — инструменты не вызывались' : status ? `run ${status.run_id}` : 'нет запуска'}</small>
      </h2>
      <div className="pipeline" role="list" aria-label="Этапы агентного цикла">
        {STAGES.map((s, i) => {
          const st = synthetic ? 'pending' : stageState(i, status)
          return (
            <div key={s.key} role="listitem" className={`stage ${st}`} aria-label={`${s.label}: ${st}`}>
              <b aria-hidden>{ICON[st]}</b>
              {s.label}
            </div>
          )
        })}
      </div>
      {events.length === 0 ? (
        <p className="unknown" style={{ marginTop: 10 }}>Журнал пуст — события появятся после реального запуска.</p>
      ) : (
        <ol className="timeline" aria-label="Журнал инструментов">
          {events.map((e) => (
            <li key={e.seq}>
              <span className="seq">{e.seq}</span>
              <div>
                <span className="tool">{e.tool}</span>
                <span className="state">{e.state}</span>
                <time>{fmtIso(e.timestamp, tz)}</time>
                <div className="sum">{e.summary}</div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
