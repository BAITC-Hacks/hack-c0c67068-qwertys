import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api, HttpError } from './api/client'
import { SYNTHETIC_TAG, syntheticEvents, syntheticForecast } from './api/synthetic'
import type {
  AgentEvent,
  Evaluation,
  ForecastResponse,
  Health,
  RunRecord,
  RunRequest,
  RunStatus,
  TurbineId,
} from './api/types'
import { AgentPanel } from './components/AgentPanel'
import { EvaluationPanel } from './components/EvaluationPanel'
import { ForecastChart } from './components/ForecastChart'
import { ForecastTable } from './components/ForecastTable'
import { ProvenanceCard } from './components/ProvenanceCard'
import { ReplayPanel } from './components/ReplayPanel'
import { fmtIso, issueTimeFromLocal, localDateHour, replayDates, tzLabel, type DisplayTz } from './lib/time'

const ALL_TURBINES: TurbineId[] = ['turbine_1', 'turbine_2']
const RUNS_KEY = 'wind-ui-runs-v1'
const POLL_MS = 1000

function loadRuns(): RunRecord[] {
  try {
    return JSON.parse(localStorage.getItem(RUNS_KEY) ?? '[]') as RunRecord[]
  } catch {
    return []
  }
}
function saveRuns(runs: RunRecord[]) {
  try {
    localStorage.setItem(RUNS_KEY, JSON.stringify(runs.slice(0, 50)))
  } catch {
    /* storage unavailable — history is per-session only */
  }
}
const sameParams = (a: RunRequest, b: RunRequest) =>
  Date.parse(a.issue_time) === Date.parse(b.issue_time) && a.horizon_hours === b.horizon_hours

function errText(e: unknown): string {
  if (e instanceof HttpError) return `${e.api?.code ?? e.status}: ${e.message}`
  return e instanceof Error ? e.message : String(e)
}

function downloadCsv(name: string, f: ForecastResponse, synthetic: boolean) {
  const head = 'run_id,turbine_id,issue_time,valid_time,lead_hours,y_pred,unit,mode'
  const lines = f.rows.map((r) =>
    [f.run_id, r.turbine_id, r.issue_time, r.valid_time, r.lead_hours, r.y_pred, f.unit, synthetic ? 'synthetic' : 'live'].join(','),
  )
  const blob = new Blob([[head, ...lines].join('\n')], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = name
  a.click()
  URL.revokeObjectURL(a.href)
}

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [healthErr, setHealthErr] = useState<string | null>(null)
  const [tz, setTz] = useState<DisplayTz>('local')
  const [date, setDate] = useState('2026-01-31')
  const [hour, setHour] = useState(17) // 17:00 UTC+5 = 12:00 UTC: 00Z run + 9 h availability rule (C3 BLOCKER 14:35)
  const [horizon, setHorizon] = useState<24 | 48>(48)
  const [shown, setShown] = useState<TurbineId[]>(ALL_TURBINES)

  const [runs, setRuns] = useState<RunRecord[]>(loadRuns)
  const [currentId, setCurrentId] = useState<string | null>(null)
  const [status, setStatus] = useState<RunStatus | null>(null)
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [forecast, setForecast] = useState<ForecastResponse | null>(null)
  const [previous, setPrevious] = useState<ForecastResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null)

  const forecastCache = useRef(new Map<string, ForecastResponse>())
  const pollRef = useRef<number | null>(null)

  const current = runs.find((r) => r.run_id === currentId) ?? null
  const synthetic = !!current?.synthetic
  const backendReady = !!health?.forecast_ready
  const request: RunRequest = useMemo(
    () => ({ issue_time: issueTimeFromLocal(date, hour), turbine_ids: ALL_TURBINES, horizon_hours: horizon }),
    [date, hour, horizon],
  )

  // Health + optional history evaluation, re-checked every 10 s.
  useEffect(() => {
    let alive = true
    const check = async () => {
      try {
        const h = await api.health()
        if (!alive) return
        setHealth(h)
        setHealthErr(null)
        api
          .runs()
          .then((list) => {
            if (!alive) return
            setRuns((local) => {
              const known = new Set(local.map((r) => r.run_id))
              const fromServer: RunRecord[] = list
                .filter((s) => !known.has(s.run_id) && s.issue_time && s.horizon_hours)
                .map((s) => ({
                  run_id: s.run_id,
                  request: { issue_time: s.issue_time!, turbine_ids: s.turbine_ids ?? ALL_TURBINES, horizon_hours: s.horizon_hours! },
                  created_at: s.started_at ?? s.updated_at ?? new Date(0).toISOString(),
                  synthetic: false,
                }))
              if (!fromServer.length) return local
              return [...local, ...fromServer].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at))
            })
          })
          .catch(() => {})
        api.evaluation().then((e) => alive && setEvaluation(e)).catch(() => alive && setEvaluation(null))
      } catch (e) {
        if (!alive) return
        setHealth(null)
        setHealthErr(errText(e))
      }
    }
    check()
    const id = window.setInterval(check, 10_000)
    return () => {
      alive = false
      window.clearInterval(id)
    }
  }, [])

  useEffect(() => saveRuns(runs), [runs])
  const runsRef = useRef(runs)
  runsRef.current = runs

  const stopPolling = () => {
    if (pollRef.current != null) window.clearTimeout(pollRef.current)
    pollRef.current = null
  }
  useEffect(() => stopPolling, [])

  const getForecast = useCallback(async (id: string) => {
    const hit = forecastCache.current.get(id)
    if (hit) return hit
    const f = await api.forecast(id)
    forecastCache.current.set(id, f)
    return f
  }, [])

  /** Previous completed live run with the same issue/horizon (for revision compare). */
  const loadPrevious = useCallback(
    async (rec: RunRecord, all: RunRecord[]) => {
      const idx = all.findIndex((r) => r.run_id === rec.run_id)
      const prev = all.slice(idx + 1).find((r) => !r.synthetic && sameParams(r.request, rec.request))
      if (!prev) return setPrevious(null)
      try {
        setPrevious(await getForecast(prev.run_id))
      } catch {
        setPrevious(null)
      }
    },
    [getForecast],
  )

  const poll = useCallback(
    async (rec: RunRecord, all: RunRecord[]) => {
      try {
        const [s, ev] = await Promise.all([api.run(rec.run_id), api.events(rec.run_id).catch(() => null)])
        setStatus(s)
        if (ev) setEvents(ev.events)
        if (s.status === 'completed') {
          setBusy(false)
          if (s.forecast_available !== false) {
            setForecast(await getForecast(rec.run_id))
            await loadPrevious(rec, all)
          }
          return
        }
        if (s.status === 'failed') {
          setBusy(false)
          setError(s.error ? `${s.error.code}: ${s.error.message}` : 'Запуск завершился ошибкой')
          return
        }
        pollRef.current = window.setTimeout(() => poll(rec, all), POLL_MS)
      } catch (e) {
        setBusy(false)
        setError(errText(e))
      }
    },
    [getForecast, loadPrevious],
  )

  const openRun = useCallback(
    (rec: RunRecord, all: RunRecord[] = runs) => {
      stopPolling()
      setCurrentId(rec.run_id)
      setError(null)
      setForecast(null)
      setPrevious(null)
      setStatus(null)
      setEvents([])
      const loc = localDateHour(rec.request.issue_time)
      setDate(loc.date)
      setHour(loc.hour)
      setHorizon(rec.request.horizon_hours)
      if (rec.synthetic) {
        setForecast(syntheticForecast(rec.run_id, rec.request))
        setEvents(syntheticEvents())
        return
      }
      setBusy(true)
      poll(rec, all)
    },
    [poll, runs],
  )

  const launch = async () => {
    setError(null)
    setBusy(true)
    try {
      const s = await api.createRun(request)
      const rec: RunRecord = { run_id: s.run_id, request, created_at: new Date().toISOString(), synthetic: false }
      const next = [rec, ...runs]
      setRuns(next)
      stopPolling()
      setCurrentId(rec.run_id)
      setStatus(s)
      setEvents([])
      setForecast(null)
      setPrevious(null)
      poll(rec, next)
    } catch (e) {
      setBusy(false)
      setError(errText(e))
    }
  }

  const launchSynthetic = () => {
    const rec: RunRecord = {
      run_id: `synthetic-${Date.now().toString(36)}`,
      request,
      created_at: new Date().toISOString(),
      synthetic: true,
    }
    const next = [rec, ...runs]
    setRuns(next)
    openRun(rec, next)
  }

  const sameIssueCount = current ? runs.filter((r) => !r.synthetic && sameParams(r.request, current.request)).length : 0
  const shownTurbines = ALL_TURBINES.filter((t) => shown.includes(t))
  const statusChip = status
    ? status.status === 'completed'
      ? 'good'
      : status.status === 'failed'
        ? 'bad'
        : 'warn'
    : ''

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <h1>Прогноз выработки ВЭС · Шелекский коридор</h1>
          <p>Агентный почасовой прогноз на 24–48 ч по архивным прогнозам погоды, доступным на момент выпуска</p>
        </div>
        <div className="chips" aria-live="polite">
          <span className={`chip ${backendReady ? 'good' : health ? 'warn' : 'bad'}`}>
            <span className="dot" />
            {backendReady ? 'Backend готов' : health ? 'Модель ещё не подключена' : 'Backend недоступен'}
          </span>
          {status && (
            <span className={`chip ${statusChip}`}>
              <span className="dot" />
              {status.status}
              {status.stage ? ` · ${status.stage}` : ''}
            </span>
          )}
          {status?.mode && <span className="chip">режим: {status.mode}</span>}
          {synthetic && <span className="chip synthetic">{SYNTHETIC_TAG}</span>}
        </div>
      </header>

      {synthetic && (
        <div className="banner synthetic" role="status">
          Показан <b>синтетический пример</b> формы данных — это не прогноз и не погода. Реальные прогнозы появятся после подключения backend.
        </div>
      )}
      {!health && healthErr && !synthetic && (
        <div className="banner info" role="status">
          {healthErr}. Запустите backend (см. README) — UI обращается к <code>/api</code> через прокси Vite.
        </div>
      )}
      {error && (
        <div className="banner error" role="alert">
          Ошибка: {error}
        </div>
      )}

      <section className="card" aria-label="Параметры запуска">
        <div className="controls">
          <label className="field">
            <span>Дата выпуска</span>
            <select value={date} onChange={(e) => setDate(e.target.value)}>
              {replayDates().map((d) => (
                <option key={d} value={d}>
                  {d.slice(8, 10)}.{d.slice(5, 7)}.{d.slice(0, 4)}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Час выпуска (UTC+5)</span>
            <select value={hour} onChange={(e) => setHour(Number(e.target.value))}>
              {Array.from({ length: 24 }, (_, h) => (
                <option key={h} value={h}>
                  {String(h).padStart(2, '0')}:00
                </option>
              ))}
            </select>
          </label>
          <div className="field">
            <span>Горизонт</span>
            <div className="seg" role="group" aria-label="Горизонт">
              {([24, 48] as const).map((h) => (
                <button key={h} type="button" aria-pressed={horizon === h} onClick={() => setHorizon(h)}>
                  {h} ч
                </button>
              ))}
            </div>
          </div>
          <div className="field">
            <span>Показать</span>
            <div className="seg" role="group" aria-label="Турбины">
              {ALL_TURBINES.map((t) => (
                <button
                  key={t}
                  type="button"
                  aria-pressed={shown.includes(t)}
                  onClick={() => setShown((s) => (s.includes(t) ? (s.length > 1 ? s.filter((x) => x !== t) : s) : [...s, t]))}
                >
                  {t === 'turbine_1' ? 'Т1' : 'Т2'}
                </button>
              ))}
            </div>
          </div>
          <div className="field">
            <span>Время</span>
            <div className="seg" role="group" aria-label="Часовой пояс отображения">
              <button type="button" aria-pressed={tz === 'local'} onClick={() => setTz('local')}>
                UTC+5
              </button>
              <button type="button" aria-pressed={tz === 'utc'} onClick={() => setTz('utc')}>
                UTC
              </button>
            </div>
          </div>
          <span className="spacer" />
          <button className="btn primary" type="button" onClick={launch} disabled={busy || !health}>
            {busy ? 'Агент работает…' : 'Запустить агента'}
          </button>
          <button
            className="btn"
            type="button"
            onClick={launch}
            disabled={busy || !health || !current || current.synthetic}
            title="Новый запуск с теми же параметрами: агент проверит, появились ли более новые входные данные; прежний результат сохраняется"
          >
            Пересчитать
          </button>
          {!backendReady && (
            <button className="btn" type="button" onClick={launchSynthetic} disabled={busy}>
              Синтетический пример
            </button>
          )}
        </div>
      </section>

      <div className="layout">
        <div className="main-col">
          <section className="card" aria-labelledby="fc-h">
            <h2 id="fc-h">
              Почасовой прогноз
              <small>
                {current
                  ? `выпуск ${fmtIso(current.request.issue_time, tz)} · ${current.request.horizon_hours} ч`
                  : `время на графике: ${tzLabel(tz)}`}
              </small>
            </h2>
            <ForecastChart
              rows={forecast?.rows ?? []}
              previous={previous?.rows}
              turbines={shownTurbines}
              issueTime={current?.request.issue_time ?? null}
              tz={tz}
              synthetic={synthetic}
            />
            {forecast && (
              <div className="controls" style={{ marginTop: 10 }}>
                {synthetic ? (
                  <button className="btn" type="button" onClick={() => downloadCsv(`${forecast.run_id}.csv`, forecast, true)}>
                    Скачать CSV (синтетика)
                  </button>
                ) : (
                  <a className="btn" href={api.exportUrl(forecast.run_id)} download style={{ display: 'inline-flex', alignItems: 'center', textDecoration: 'none' }}>
                    Скачать CSV
                  </a>
                )}
                <span style={{ color: 'var(--ink-2)', fontSize: 12.5 }}>
                  {forecast.rows.length} строк · единица: {forecast.unit}
                  {previous ? ` · сравнение с предыдущей версией (${previous.run_id})` : sameIssueCount > 1 ? '' : ' · для сравнения версий нажмите «Пересчитать»'}
                </span>
              </div>
            )}
          </section>

          {forecast && (
            <section className="card" aria-labelledby="tbl-h">
              <h2 id="tbl-h">Таблица</h2>
              <ForecastTable rows={forecast.rows} previous={previous?.rows} turbines={shownTurbines} tz={tz} />
            </section>
          )}

          <ReplayPanel
            hour={hour}
            tz={tz}
            turbines={shownTurbines}
            enabled={!!health && !busy}
            onRun={(rec) => setRuns((rs) => [rec, ...rs])}
            onOpen={(id) => {
              const rec = runsRef.current.find((r) => r.run_id === id)
              if (rec) openRun(rec, runsRef.current)
            }}
          />

          <EvaluationPanel evaluation={evaluation} />
        </div>

        <aside className="side-col">
          <AgentPanel status={status} events={events} tz={tz} synthetic={synthetic} />
          <ProvenanceCard metadata={forecast?.metadata ?? null} status={status} issueTime={current?.request.issue_time ?? null} tz={tz} />
          <section className="card" aria-labelledby="runs-h">
            <h2 id="runs-h">
              Запуски <small>сервер + этот браузер</small>
            </h2>
            {runs.length === 0 ? (
              <p className="unknown">Запусков ещё не было.</p>
            ) : (
              <ul className="runs">
                {runs.slice(0, 12).map((r) => (
                  <li key={r.run_id}>
                    <button type="button" aria-current={r.run_id === currentId} onClick={() => openRun(r)}>
                      {r.synthetic ? '⚗ ' : ''}
                      {fmtIso(r.request.issue_time, tz)} · {r.request.horizon_hours} ч
                      <div className="meta">
                        {r.synthetic ? 'синтетика' : r.run_id} · создан {fmtIso(r.created_at, tz)}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </aside>
      </div>

      <footer className="foot">
        Мощность — нормализованная, как в исходных SCADA (номинал неизвестен), не МВт. Погода: только прогнозы, доступные на момент выпуска. Данные Open-Meteo (CC BY 4.0).
      </footer>
    </div>
  )
}
