import { useEffect, useRef, useState } from 'react'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api, HttpError } from '../api/client'
import type { ForecastResponse, ForecastRow, RunRecord, RunRequest, TurbineId } from '../api/types'
import { fmtDayHour, issueTimeFromLocal, replayDates, type DisplayTz } from '../lib/time'
import { ChartTip, TURBINE_LABEL } from './ForecastChart'

type CellState = 'pending' | 'running' | 'completed' | 'failed'
interface Cell {
  date: string
  state: CellState
  run_id?: string
  error?: string
  rows?: ForecastRow[]
}

// February target calendar = SCADA clock (fixed UTC+6, inferred), same as the team replay export (C3 faab55c)
const FEB_START = Date.parse('2026-02-01T00:00:00+06:00')
const FEB_END = Date.parse('2026-03-01T00:00:00+06:00')
const FEB_HOURS = (FEB_END - FEB_START) / 3600_000 // 672
const COLOR: Record<TurbineId, string> = { turbine_1: 'var(--t1)', turbine_2: 'var(--t2)' }
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

interface Props {
  hour: number
  tz: DisplayTz
  turbines: TurbineId[]
  enabled: boolean
  onRun: (rec: RunRecord) => void
  onOpen: (run_id: string) => void
  /** Real runs already stored by the API (server list + this browser). */
  saved: RunRecord[]
  /** Deep link ?replay=saved: fill the panel from saved runs once on load. */
  autoLoadSaved?: boolean
}

/** For each (turbine, valid hour) keep the row from the most recent issue (smallest lead). */
function stitch(cells: Cell[]) {
  const best = new Map<string, ForecastRow>()
  for (const c of cells)
    for (const r of c.rows ?? []) {
      if (r.y_pred == null) continue // missing hour: fall back to an older issue, never to zero
      const k = `${r.turbine_id}|${Date.parse(r.valid_time)}`
      const cur = best.get(k)
      if (!cur || r.lead_hours < cur.lead_hours) best.set(k, r)
    }
  const byT = new Map<number, { t: number } & Record<string, number | null>>()
  const covered: Record<string, number> = { turbine_1: 0, turbine_2: 0 }
  for (const r of best.values()) {
    const t = Date.parse(r.valid_time)
    if (t < FEB_START || t >= FEB_END) continue
    covered[r.turbine_id]++
    const p = byT.get(t) ?? { t }
    p[r.turbine_id] = r.y_pred
    p[`lead_${r.turbine_id}`] = r.lead_hours
    byT.set(t, p)
  }
  return { points: [...byT.values()].sort((a, b) => a.t - b.t), covered }
}

export function ReplayPanel({ hour, tz, turbines, enabled, onRun, onOpen, saved, autoLoadSaved }: Props) {
  const [cells, setCells] = useState<Cell[]>(() => replayDates().map((date) => ({ date, state: 'pending' })))
  const [running, setRunning] = useState(false)
  const stopRef = useRef(false)

  const update = (i: number, patch: Partial<Cell>) => setCells((cs) => cs.map((c, j) => (j === i ? { ...c, ...patch } : c)))

  /** Rebuild the grid from completed runs already stored by the API — no new POSTs. */
  const loadSaved = async () => {
    setRunning(true)
    const dates = replayDates()
    setCells(dates.map((date) => ({ date, state: 'pending' })))
    for (let i = 0; i < dates.length; i++) {
      const at = Date.parse(issueTimeFromLocal(dates[i], hour))
      const cand = saved.filter((r) => !r.synthetic && r.request.horizon_hours === 48 && Date.parse(r.request.issue_time) === at)
      let filled = false
      for (const r of cand) {
        try {
          const f = await api.forecast(r.run_id) // 409/404 for failed or unknown runs -> try the next one
          update(i, { state: 'completed', run_id: r.run_id, rows: f.rows })
          filled = true
          break
        } catch {
          /* not completed */
        }
      }
      if (!filled) update(i, { state: 'pending', error: 'сохранённого завершённого выпуска нет' })
    }
    setRunning(false)
  }
  const autoDone = useRef(false)
  useEffect(() => {
    if (!autoLoadSaved || autoDone.current || !enabled || !saved.length) return
    autoDone.current = true
    loadSaved()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoLoadSaved, enabled, saved.length])

  const runAll = async () => {
    stopRef.current = false
    setRunning(true)
    const dates = replayDates()
    setCells(dates.map((date) => ({ date, state: 'pending' })))
    for (let i = 0; i < dates.length && !stopRef.current; i++) {
      const req: RunRequest = { issue_time: issueTimeFromLocal(dates[i], hour), turbine_ids: ['turbine_1', 'turbine_2'], horizon_hours: 48 }
      update(i, { state: 'running' })
      try {
        let s = await api.createRun(req)
        onRun({ run_id: s.run_id, request: req, created_at: new Date().toISOString(), synthetic: false })
        update(i, { run_id: s.run_id })
        // bounded polling; Stop is honoured inside a run too (the run itself keeps going on the server)
        for (let k = 0; (s.status === 'queued' || s.status === 'running') && !stopRef.current; k++) {
          if (k > 900) throw new Error('timeout: нет результата за ~10 мин')
          await sleep(700)
          s = await api.run(s.run_id)
        }
        if (stopRef.current && (s.status === 'queued' || s.status === 'running')) {
          update(i, { state: 'pending', error: 'остановлено пользователем, запуск продолжается на сервере' })
          break
        }
        if (s.status === 'failed') {
          update(i, { state: 'failed', error: s.error ? `${s.error.code}: ${s.error.message}` : 'failed' })
          continue
        }
        const f: ForecastResponse = await api.forecast(s.run_id)
        update(i, { state: 'completed', rows: f.rows })
      } catch (e) {
        update(i, { state: 'failed', error: e instanceof HttpError ? `${e.api?.code ?? e.status}: ${e.message}` : String(e) })
      }
    }
    setRunning(false)
  }

  const { points, covered } = stitch(cells)
  const done = cells.filter((c) => c.state === 'completed').length
  const failed = cells.filter((c) => c.state === 'failed').length

  const exportAll = () => {
    const head = 'run_id,turbine_id,issue_time,valid_time,lead_hours,y_pred,unit'
    const lines = cells.flatMap((c) =>
      (c.rows ?? []).map((r) => [c.run_id, r.turbine_id, r.issue_time, r.valid_time, r.lead_hours, r.y_pred, 'normalized_power'].join(',')),
    )
    const blob = new Blob([[head, ...lines].join('\n')], { type: 'text/csv;charset=utf-8' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'forecast_feb2026_all_issues.csv'
    a.click()
    URL.revokeObjectURL(a.href)
  }

  return (
    <section className="card" aria-labelledby="replay-h">
      <h2 id="replay-h">
        Реплей февраля 2026
        <small>29 выпусков 31.01–28.02 в {String(hour).padStart(2, '0')}:00 UTC+5, горизонт 48 ч, каждый — отдельный запуск агента</small>
      </h2>
      <div className="controls">
        <button className="btn primary" type="button" onClick={runAll} disabled={!enabled || running}>
          {running ? `Идёт… ${done + failed}/29` : 'Прогнать весь февраль'}
        </button>
        {running && (
          <button className="btn" type="button" onClick={() => (stopRef.current = true)}>
            Остановить
          </button>
        )}
        <button className="btn" type="button" onClick={exportAll} disabled={!done}>
          CSV всех выпусков
        </button>
        <button className="btn" type="button" onClick={loadSaved} disabled={!enabled || running} title="Собрать сетку из уже выполненных и сохранённых сервером запусков (без новых расчётов)">
          Показать сохранённые выпуски
        </button>
        <span style={{ color: 'var(--ink-2)', fontSize: 12.5 }}>
          готово {done}/29{failed ? ` · ошибок ${failed}` : ''} · покрытие февраля: Т1 {covered.turbine_1}/{FEB_HOURS} ч, Т2 {covered.turbine_2}/{FEB_HOURS} ч
        </span>
      </div>

      <div className="replay-grid" role="list" aria-label="Статусы выпусков">
        {cells.map((c) => (
          <button
            key={c.date}
            type="button"
            role="listitem"
            className={`rcell ${c.state}`}
            disabled={!c.run_id}
            onClick={() => c.run_id && onOpen(c.run_id)}
            title={`${c.date}: ${c.state}${c.error ? ` — ${c.error}` : ''}`}
          >
            {c.date.slice(8, 10)}.{c.date.slice(5, 7)}
          </button>
        ))}
      </div>

      {points.length > 0 && (
        <>
          <div className="chart-wrap" style={{ height: 260, marginTop: 10 }} role="img" aria-label="Склеенный прогноз на февраль">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={points} margin={{ top: 8, right: 16, bottom: 4, left: 0 }}>
                <CartesianGrid stroke="var(--grid)" strokeDasharray="2 4" vertical={false} />
                <XAxis
                  dataKey="t"
                  type="number"
                  scale="time"
                  domain={[FEB_START, FEB_END]}
                  tickFormatter={(v: number) => fmtDayHour(v, tz).slice(0, 5)}
                  stroke="var(--axis)"
                  tick={{ fill: 'var(--muted)', fontSize: 11 }}
                  minTickGap={30}
                />
                <YAxis domain={[0, (max: number) => Math.max(1, Math.ceil(max * 10) / 10)]} tickCount={5} stroke="var(--axis)" tick={{ fill: 'var(--muted)', fontSize: 11 }} width={40} />
                <Tooltip
                  content={(p) => <ChartTip active={p.active} payload={p.payload} label={p.label} tz={tz} />}
                  cursor={{ stroke: 'var(--ink-2)', strokeWidth: 1, strokeDasharray: '2 3' }}
                />
                {turbines.map((t) => (
                  <Line key={t} dataKey={t} name={TURBINE_LABEL[t]} stroke={COLOR[t]} strokeWidth={1.5} dot={false} isAnimationActive={false} connectNulls={false} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="legend-note">
            Для каждого часа февраля (календарь SCADA, UTC+6) взят прогноз самого свежего выпуска (наименьшее упреждение ≥ 1 ч). Полный журнал всех 48-ч горизонтов с перекрытиями — в «CSV всех выпусков». Фактических значений за февраль нет, поэтому точность здесь не считается.
          </p>
        </>
      )}
    </section>
  )
}
