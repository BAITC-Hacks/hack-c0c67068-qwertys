import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api, HttpError } from './api/client'
import { SYNTHETIC_TAG, syntheticEvents, syntheticForecast } from './api/synthetic'
import type {
  AgentEvent,
  ForecastResponse,
  Health,
  RunRecord,
  RunRequest,
  RunStatus,
  TurbineId,
} from './api/types'
import { AgentPanel } from './components/AgentPanel'
import { EvaluationPanel, type EvaluationV1 } from './components/EvaluationPanel'
import { HourDial } from './components/HourDial'
import { IssueCalendar } from './components/IssueCalendar'
import { ForecastChart } from './components/ForecastChart'
import { ForecastTable } from './components/ForecastTable'
import { KpiStrip } from './components/KpiStrip'
import { TrustStrip } from './components/TrustStrip'
import { ProvenanceCard } from './components/ProvenanceCard'
import { ReplayPanel } from './components/ReplayPanel'
import { Mark } from './components/SiteHeader'
import { Dock, DockTabs, Icon, Rail, useMedia, usePersisted, type RailItem } from './components/Workspace'
import { CACHED_ISSUE_HOUR_LOCAL, cachedIssueTime, isSupportedCachedIssue, nextCachedIssue, fmtIso, localDateHour, replayDates, tzLabel, type DisplayTz } from './lib/time'

const ALL_TURBINES: TurbineId[] = ['turbine_1', 'turbine_2']
const RUNS_KEY = 'wind-ui-runs-v1'
const POLL_MS = 1000

// Workspace: rail sections (main panel) + two docks; on phones the docks become sections too.
type Section = 'forecast' | 'table' | 'replay' | 'quality'
type View = Section | 'params' | 'agent'
const SECTIONS: Section[] = ['forecast', 'table', 'replay', 'quality']
const VIEWS: View[] = ['params', ...SECTIONS, 'agent']
type SideTab = 'agent' | 'prov' | 'runs'
// docks overlay the main panel below these widths (kept in sync with index.css)
const RIGHT_OVERLAY = '(max-width: 1279px)'
const LEFT_OVERLAY = '(max-width: 1023px)'
const MOBILE = '(max-width: 760px)'
const FOOTNOTE =
  'Агентный почасовой прогноз на 24–48 ч по архивным прогнозам погоды, которые по правилу доступности (допущение) вышли до момента выпуска. Мощность — нормализованная, как в исходных SCADA (номинал неизвестен), не МВт. Погода: одна ячейка ECMWF (43.62° N 78.48° E, 555 м), только прогнозы, отобранные по правилу доступности к моменту выпуска (время доступности — допущение, не подтверждённый журнал публикации). Данные Open-Meteo (CC BY 4.0).'

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
  const [horizon, setHorizon] = useState<24 | 48>(48)
  const [shown, setShown] = useState<TurbineId[]>(ALL_TURBINES)

  const [runs, setRuns] = useState<RunRecord[]>(loadRuns)
  const [currentId, setCurrentId] = useState<string | null>(null)
  const [status, setStatus] = useState<RunStatus | null>(null)
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [forecast, setForecast] = useState<ForecastResponse | null>(null)
  const [previous, setPrevious] = useState<ForecastResponse | null>(null)
  const [compareId, setCompareId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [evaluation, setEvaluation] = useState<EvaluationV1 | null>(null)
  const [evaluationV2, setEvaluationV2] = useState<EvaluationV1 | null>(null)

  const rightOverlay = useMedia(RIGHT_OVERLAY)
  const leftOverlay = useMedia(LEFT_OVERLAY)
  const mobile = useMedia(MOBILE)
  const [view, setView] = usePersisted<View>('wind-ui-view', 'forecast', VIEWS)
  const [leftOpen, setLeftOpen] = useState(!leftOverlay)
  const [rightOpen, setRightOpen] = useState(!rightOverlay)
  const [sideTab, setSideTab] = useState<SideTab>('agent')
  // crossing a breakpoint resets the docks: in-flow docks open, overlay docks closed (adjusted during render, no effect)
  const [seenLeft, setSeenLeft] = useState(leftOverlay)
  if (seenLeft !== leftOverlay) {
    setSeenLeft(leftOverlay)
    setLeftOpen(!leftOverlay)
  }
  const [seenRight, setSeenRight] = useState(rightOverlay)
  if (seenRight !== rightOverlay) {
    setSeenRight(rightOverlay)
    setRightOpen(!rightOverlay)
  }
  const mainView: Section = view === 'params' || view === 'agent' ? 'forecast' : view
  /** After a launch/open: show the forecast and the agent log, close docks that cover it. */
  const focusResult = useCallback(() => {
    setView((v) => (v === 'table' ? v : 'forecast'))
    setSideTab('agent')
    if (leftOverlay) setLeftOpen(false)
  }, [setView, leftOverlay])

  // Keys: 1–4 sections, [ and ] toggle docks, Esc closes overlay docks.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.altKey || e.ctrlKey || e.metaKey) return
      const t = e.target
      if (t instanceof HTMLElement && t.closest('input, select, textarea, [contenteditable="true"]')) return
      // physical keys, so the shortcuts also work in the Russian layout ([ is «х» there)
      const i = ['Digit1', 'Digit2', 'Digit3', 'Digit4'].indexOf(e.code)
      if (i >= 0) setView(SECTIONS[i])
      else if (e.code === 'BracketLeft') setLeftOpen((o) => !o)
      else if (e.code === 'BracketRight') setRightOpen((o) => !o)
      else if (e.key === 'Escape') {
        if (leftOverlay) setLeftOpen(false)
        if (rightOverlay) setRightOpen(false)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [setView, leftOverlay, rightOverlay])

  const forecastCache = useRef(new Map<string, ForecastResponse>())
  const pollRef = useRef<number | null>(null)
  // Generation guard: responses for a run the user has navigated away from are dropped.
  const genRef = useRef(0)

  const current = runs.find((r) => r.run_id === currentId) ?? null
  const synthetic = !!current?.synthetic
  const backendReady = !!health?.forecast_ready
  const request: RunRequest = useMemo(
    () => ({ issue_time: cachedIssueTime(date), turbine_ids: ALL_TURBINES, horizon_hours: horizon }),
    [date, horizon],
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
        api
          .evaluationV2()
          // only accept a report that really is a different (post-test) experiment
          .then((e) => alive && setEvaluationV2(e?.experiment_label || e?.january_test_previously_viewed ? e : null))
          .catch(() => alive && setEvaluationV2(null))
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
    genRef.current++
  }
  useEffect(() => stopPolling, [])

  const getForecast = useCallback(async (id: string) => {
    const hit = forecastCache.current.get(id)
    if (hit) return hit
    const f = await api.forecast(id)
    forecastCache.current.set(id, f)
    return f
  }, [])

  /** Load any saved run as the comparison layer (only real runs; common valid hours are matched later). */
  const compareGen = useRef(0)
  // When set, the next completed run is compared with this run instead of the default previous version.
  const pendingCompare = useRef<string | null>(null)
  const selectCompare = useCallback(
    async (id: string | null) => {
      const gen = ++compareGen.current // only the latest comparison request may write state
      setCompareId(id)
      if (!id) return setPrevious(null)
      try {
        const f = await getForecast(id)
        if (gen === compareGen.current) setPrevious(f)
      } catch (e) {
        if (gen !== compareGen.current) return
        setPrevious(null)
        setCompareId(null)
        setError(`Сравнение недоступно: ${errText(e)}`)
      }
    },
    [getForecast],
  )

  /** Default comparison: previous completed live run with the same issue/horizon (recompute). */
  const loadPrevious = useCallback(
    async (rec: RunRecord, all: RunRecord[]) => {
      const idx = all.findIndex((r) => r.run_id === rec.run_id)
      const prev = all.slice(idx + 1).find((r) => !r.synthetic && sameParams(r.request, rec.request))
      await selectCompare(prev?.run_id ?? null)
    },
    [selectCompare],
  )

  const poll = useCallback(
    async (rec: RunRecord, all: RunRecord[], gen: number) => {
      const stale = () => gen !== genRef.current
      try {
        const [s, ev] = await Promise.all([api.run(rec.run_id), api.events(rec.run_id).catch(() => null)])
        if (stale()) return
        setStatus(s)
        if (ev) setEvents(ev.events)
        if (s.status === 'completed') {
          if (s.forecast_available !== false) {
            const f = await getForecast(rec.run_id)
            if (stale()) return
            setForecast(f)
            const target = pendingCompare.current
            pendingCompare.current = null
            if (target && target !== rec.run_id) await selectCompare(target)
            else await loadPrevious(rec, all)
          }
          if (!stale()) setBusy(false)
          return
        }
        if (s.status === 'failed') {
          setBusy(false)
          setError(s.error ? `${s.error.code}: ${s.error.message}` : 'Запуск завершился ошибкой')
          return
        }
        pollRef.current = window.setTimeout(() => poll(rec, all, gen), POLL_MS)
      } catch (e) {
        if (stale()) return
        setBusy(false)
        setError(errText(e))
      }
    },
    [getForecast, loadPrevious, selectCompare],
  )

  const openRun = useCallback(
    (rec: RunRecord, all: RunRecord[] = runs) => {
      stopPolling()
      focusResult()
      setCurrentId(rec.run_id)
      setError(null)
      setForecast(null)
      setPrevious(null)
      setCompareId(null)
      compareGen.current++
      setStatus(null)
      setEvents([])
      const loc = localDateHour(rec.request.issue_time)
      setDate(loc.date)
      setHorizon(rec.request.horizon_hours)
      if (rec.synthetic) {
        setBusy(false)
        setForecast(syntheticForecast(rec.run_id, rec.request))
        setEvents(syntheticEvents())
        return
      }
      setBusy(true)
      poll(rec, all, genRef.current)
    },
    [poll, runs, focusResult],
  )

  const launch = async (req: RunRequest = request, compareWith: string | null = null) => {
    if (!isSupportedCachedIssue(req.issue_time)) {
      setError('Для подготовленного кэша выберите дату 31.01–28.02 и выпуск 17:00 UTC+5 (12:00 UTC). Сохранённый результат доступен для просмотра.')
      return
    }
    setError(null)
    setBusy(true)
    focusResult()
    pendingCompare.current = compareWith
    try {
      const s = await api.createRun(req)
      const rec: RunRecord = { run_id: s.run_id, request: req, created_at: new Date().toISOString(), synthetic: false }
      const next = [rec, ...runs]
      setRuns(next)
      stopPolling()
      setCurrentId(rec.run_id)
      setStatus(s)
      setEvents([])
      setForecast(null)
      setPrevious(null)
      setCompareId(null)
      compareGen.current++
      poll(rec, next, genRef.current)
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

  /** Honest input update: same target hours, later issue that can use a newer ECMWF run (cache has one 00Z run/day). */
  const nextIssue = current && !current.synthetic ? nextCachedIssue(current.request.issue_time) : null
  const nextIssueOk = !!nextIssue
  const updateWeather = () => {
    if (!current || !nextIssue) return
    const req: RunRequest = { ...current.request, issue_time: nextIssue }
    const loc = localDateHour(req.issue_time)
    setDate(loc.date)
    launch(req, current.run_id)
  }

  // Deep links: ?run=<id>&compare=<id>&tz=local|scada|utc (reproducible demo/evidence frames)
  const deepLinkDone = useRef(false)
  useEffect(() => {
    if (deepLinkDone.current || !health) return
    const qs = new URLSearchParams(window.location.search)
    const tzq = qs.get('tz')
    if (tzq === 'local' || tzq === 'scada' || tzq === 'utc') setTz(tzq)
    const rid = qs.get('run')
    if (!rid) {
      deepLinkDone.current = true
      return
    }
    const rec = runs.find((r) => r.run_id === rid)
    if (!rec) return // wait for server run list
    deepLinkDone.current = true
    pendingCompare.current = qs.get('compare')
    openRun(rec, runs)
  }, [health, runs, openRun])
  useEffect(() => {
    if (!deepLinkDone.current) return
    const qs = new URLSearchParams()
    if (currentId && !current?.synthetic) qs.set('run', currentId)
    if (compareId) qs.set('compare', compareId)
    if (tz !== 'local') qs.set('tz', tz)
    const url = `${window.location.pathname}${qs.toString() ? `?${qs}` : ''}${window.location.hash}`
    window.history.replaceState(null, '', url)
  }, [currentId, compareId, tz, current?.synthetic])

  const retry = () => {
    if (current && !current.synthetic) {
      setDate(localDateHour(current.request.issue_time).date)
      setHorizon(current.request.horizon_hours)
      launch(current.request)
    } else launch()
  }

  /** Other real runs whose valid window overlaps the current one. */
  const compareCandidates = current
    ? runs.filter((r) => {
        if (r.synthetic || r.run_id === current.run_id) return false
        const a0 = Date.parse(current.request.issue_time)
        const a1 = a0 + current.request.horizon_hours * 3600_000
        const b0 = Date.parse(r.request.issue_time)
        const b1 = b0 + r.request.horizon_hours * 3600_000
        return b0 < a1 && a0 < b1
      })
    : []

  const sameIssueCount = current ? runs.filter((r) => !r.synthetic && sameParams(r.request, current.request)).length : 0
  const shownTurbines = ALL_TURBINES.filter((t) => shown.includes(t))
  const statusChip = status
    ? status.status === 'completed'
      ? 'good'
      : status.status === 'failed'
        ? 'bad'
        : 'warn'
    : ''

  const csvButton = !forecast ? (
    <button className="btn" type="button" disabled title="CSV появится после расчёта">
      CSV
    </button>
  ) : synthetic ? (
    <button className="btn" type="button" onClick={() => downloadCsv(`${forecast.run_id}.csv`, forecast, true)}>
      CSV (синтетика)
    </button>
  ) : (
    <a className="btn" href={api.exportUrl(forecast.run_id)} download>
      Скачать CSV
    </a>
  )

  const runSummary = `${date.slice(8, 10)}.${date.slice(5, 7)} 17:00 UTC+5 · ${horizon} ч`
  const railItems: RailItem<View>[] = [
    ...(mobile ? [{ key: 'params' as const, label: 'Запуск', icon: Icon.params }] : []),
    { key: 'forecast', label: 'Прогноз', icon: Icon.forecast, hint: 'клавиша 1', badge: busy ? 'busy' : forecast ? 'ready' : null },
    { key: 'table', label: 'Ведомость', icon: Icon.table, hint: 'клавиша 2' },
    { key: 'replay', label: 'Реплей', icon: Icon.replay, hint: 'февраль, клавиша 3' },
    { key: 'quality', label: 'Качество', icon: Icon.quality, hint: 'на истории, клавиша 4' },
    ...(mobile ? [{ key: 'agent' as const, label: 'Агент', icon: Icon.agent, badge: events.length }] : []),
  ]
  const overlayOpen = !mobile && ((leftOverlay && leftOpen) || (rightOverlay && rightOpen))

  return (
    <div className="dash">
      <header className="topbar">
        <span className="brand">
          <Mark />
          SAMAL
        </span>
        <div className="topbar-title">
          <h1>Прогноз выработки ВЭС</h1>
          <span className="dash-site" title="прогноз погоды: одна ячейка ECMWF (43.62° N 78.48° E, 555 м)">
            Шелекский коридор · <i className="pin t1" aria-hidden />Т1 43.6452° N 78.5356° E · <i className="pin t2" aria-hidden />Т2 43.6432° N 78.5388° E
          </span>
        </div>
        <span className="spacer" />
        <div className="chips" aria-live="polite">
          <span className={`chip ${backendReady ? 'good' : health ? 'warn' : 'bad'}`}>
            <span className="dot" />
            {backendReady ? 'backend готов' : health ? 'модель ещё не подключена' : 'backend недоступен'}
          </span>
          {status && (
            <span className={`chip ${statusChip}`}>
              <span className="dot" />
              {status.status}
              {status.stage ? ` · ${status.stage}` : ''}
            </span>
          )}
          {status?.mode && <span className="chip">режим {status.mode}</span>}
          <span className="chip">время {tzLabel(tz)}</span>
          {synthetic && <span className="chip synthetic">{SYNTHETIC_TAG}</span>}
        </div>
        <a className="site-nav" href="#/">
          Главная
        </a>
      </header>

      <div className="ws" data-left={leftOpen ? 'open' : 'closed'} data-right={rightOpen ? 'open' : 'closed'} data-view={view}>
        <Rail
          items={railItems}
          active={mobile ? view : mainView}
          onSelect={setView}
          tools={
            !mobile && (
              <>
                <button type="button" className="rail-btn" aria-pressed={leftOpen} aria-controls="dock-params" onClick={() => setLeftOpen((o) => !o)} title="Панель «Параметры запуска» · клавиша [">
                  <span className="rail-ico">{Icon.params}</span>
                  <span className="rail-label">Параметры</span>
                </button>
                <button type="button" className="rail-btn" aria-pressed={rightOpen} aria-controls="dock-agent" onClick={() => setRightOpen((o) => !o)} title="Панель «Агент и данные» · клавиша ]">
                  <span className="rail-ico">
                    {Icon.agent}
                    {busy && <i className="rail-badge busy" aria-label="агент работает" />}
                  </span>
                  <span className="rail-label">Агент</span>
                </button>
              </>
            )
          }
        />

        {/* ---------- left dock: what to forecast ---------- */}
        <Dock
          id="dock-params"
          side="left"
          title="Параметры запуска"
          icon={Icon.params}
          open={mobile || leftOpen}
          hidden={mobile && view !== 'params'}
          collapsible={!mobile}
          onToggle={() => setLeftOpen((o) => !o)}
          footer={
            <>
              <p className="launch-sum">
                Выпуск <b>{runSummary}</b>
              </p>
              <button className="btn primary wide" type="button" onClick={() => launch()} disabled={busy || !health}>
                {busy ? 'Агент работает…' : 'Запустить агента'}
              </button>
              {!backendReady && (
                <button className="btn wide" type="button" onClick={launchSynthetic} disabled={busy}>
                  Синтетический пример
                </button>
              )}
            </>
          }
        >
          <IssueCalendar value={date} dates={replayDates()} onChange={setDate} />
          <section className="card" aria-labelledby="run-h">
            <h2 id="run-h">Выпуск и горизонт</h2>
            <div className="run-grid">
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
                <span>Выпуск</span>
                <output className="issue-readout">
                  {date.slice(8, 10)}.{date.slice(5, 7)} 17:00
                </output>
              </div>
            </div>
          </section>
          <section className="card" aria-labelledby="show-h">
            <h2 id="show-h">Отображение</h2>
            <div className="run-grid">
              <div className="field">
                <span>Турбины</span>
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
                  <button type="button" aria-pressed={tz === 'local'} onClick={() => setTz('local')} title="UTC+5">
                    +5
                  </button>
                  <button type="button" aria-pressed={tz === 'scada'} onClick={() => setTz('scada')} title="Часы SCADA (фиксированный UTC+6, допущение)">
                    +6
                  </button>
                  <button type="button" aria-pressed={tz === 'utc'} onClick={() => setTz('utc')}>
                    UTC
                  </button>
                </div>
              </div>
            </div>
          </section>
          <HourDial hour={CACHED_ISSUE_HOUR_LOCAL} />
        </Dock>

        {/* ---------- main panel: the active section ---------- */}
        <main className="main-panel" hidden={mobile && (view === 'params' || view === 'agent')}>
          {(synthetic || (!health && healthErr) || error) && (
            <div className="banners">
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
                  <span>Ошибка: {error}</span>
                  <span className="banner-actions">
                    {current && !current.synthetic && (
                      <button className="btn" type="button" onClick={retry} disabled={busy || !health || !isSupportedCachedIssue(current.request.issue_time)}>
                        Повторить запуск
                      </button>
                    )}
                    <button className="btn" type="button" onClick={() => setError(null)}>
                      Скрыть
                    </button>
                  </span>
                </div>
              )}
            </div>
          )}

          {mainView === 'forecast' && (
            <section className="view view-forecast" aria-labelledby="fc-h">
              <div className="view-head">
                <h2 id="fc-h">
                  Почасовой прогноз
                  <small>
                    {current
                      ? `выпуск ${fmtIso(current.request.issue_time, tz)} · ${current.request.horizon_hours} ч`
                      : `время на графике: ${tzLabel(tz)}`}
                  </small>
                </h2>
                <div className="view-actions">
                  <button
                    className="btn"
                    type="button"
                    onClick={() => launch()}
                    disabled={busy || !health || !current || current.synthetic}
                    title="Новый запуск с параметрами формы в 17:00 UTC+5; прежний результат сохраняется"
                  >
                    Пересчитать
                  </button>
                  <button
                    className="btn"
                    type="button"
                    onClick={updateWeather}
                    disabled={busy || !backendReady || !current || current.synthetic || !nextIssueOk}
                    title={
                      nextIssueOk
                        ? 'Новый выпуск на 24 ч позже: агент берёт более свежий прогон ECMWF и пересчитывает те же целевые часы; прежний результат сохраняется и накладывается пунктиром'
                        : 'Доступно для выпусков в 17:00 UTC+5; последний выпуск — 28.02'
                    }
                  >
                    Обновить погоду (+24 ч)
                  </button>
                  {csvButton}
                </div>
              </div>
              {forecast && <KpiStrip rows={forecast.rows} turbines={shownTurbines} tz={tz} />}
              {forecast && !synthetic && (
                <TrustStrip
                  metadata={forecast.metadata}
                  status={status}
                  rows={forecast.rows}
                  horizon={current?.request.horizon_hours ?? horizon}
                  turbines={ALL_TURBINES.length}
                  tz={tz}
                  synthetic={synthetic}
                />
              )}
              <div className="fc-chart">
                <ForecastChart
                  rows={forecast?.rows ?? []}
                  previous={previous?.rows}
                  turbines={shownTurbines}
                  issueTime={current?.request.issue_time ?? null}
                  tz={tz}
                  synthetic={synthetic}
                  loadingStage={busy && !forecast ? (status?.stage ?? '') : null}
                />
              </div>
              {forecast && (
                <div className="controls fc-foot">
                  {!synthetic && (
                    <label className="field compare">
                      <span>Сравнить с запуском</span>
                      <select
                        value={compareId ?? ''}
                        onChange={(e) => selectCompare(e.target.value || null)}
                        disabled={!compareCandidates.length}
                        title={compareCandidates.length ? 'Наложить другой сохранённый запуск на общие часы' : 'Нет другого сохранённого запуска с общими часами — нажмите «Пересчитать» или запустите соседнюю дату'}
                      >
                        <option value="">{compareCandidates.length ? '— без сравнения —' : 'нет запусков с общими часами'}</option>
                        {compareCandidates.map((r) => (
                          <option key={r.run_id} value={r.run_id}>
                            {sameParams(r.request, current!.request) ? 'та же дата · ' : 'выпуск '}
                            {fmtIso(r.request.issue_time, tz)} · {r.run_id.slice(0, 10)}
                          </option>
                        ))}
                      </select>
                    </label>
                  )}
                  <span className="fc-note">
                    {forecast.rows.length} строк · единица: {forecast.unit}
                    {previous
                      ? ` · пунктир и Δ: ${previous.run_id.slice(0, 10)} (прогон погоды ${fmtIso(previous.metadata.weather_run_time, tz) ?? '?'}) vs текущий (прогон ${fmtIso(forecast.metadata.weather_run_time, tz) ?? '?'})`
                      : sameIssueCount > 1
                        ? ''
                        : ' · «Обновить погоду (+24 ч)» пересчитает те же часы по более свежему прогону'}
                  </span>
                </div>
              )}
            </section>
          )}

          {mainView === 'table' && (
            <section className="view view-table" aria-labelledby="tbl-h">
              <div className="view-head">
                <h2 id="tbl-h">
                  Почасовая ведомость
                  <small>
                    {forecast
                      ? `${forecast.rows.length} строк · ${forecast.unit} · время ${tzLabel(tz)}${previous ? ' · Δ к сравниваемому запуску' : ''}`
                      : 'нет рассчитанного прогноза'}
                  </small>
                </h2>
                <div className="view-actions">{csvButton}</div>
              </div>
              {forecast ? (
                <ForecastTable rows={forecast.rows} previous={previous?.rows} turbines={shownTurbines} tz={tz} />
              ) : (
                <div className="empty">{busy ? 'Агент считает прогноз — ведомость появится после расчёта.' : 'Ведомость появится после расчёта. Выберите дату выпуска и запустите агента.'}</div>
              )}
            </section>
          )}

          {/* stateful panels stay mounted so a running February replay survives switching sections */}
          <div className="view" hidden={mainView !== 'replay'}>
            <ReplayPanel
              saved={runs}
              autoLoadSaved={new URLSearchParams(window.location.search).get('replay') === 'saved'}
              hour={CACHED_ISSUE_HOUR_LOCAL}
              tz={tz}
              turbines={shownTurbines}
              enabled={!!health && !busy}
              onRun={(rec) => setRuns((rs) => [rec, ...rs])}
              onOpen={(id) => {
                const rec = runsRef.current.find((r) => r.run_id === id)
                if (rec) openRun(rec, runsRef.current)
              }}
            />
          </div>
          <div className="view" hidden={mainView !== 'quality'}>
            <EvaluationPanel evaluation={evaluation} evaluationV2={evaluationV2} currentModel={forecast?.metadata.model_version ?? null} />
          </div>
        </main>

        {/* ---------- right dock: how the agent got there ---------- */}
        <Dock
          id="dock-agent"
          side="right"
          title="Агент и данные"
          icon={Icon.agent}
          open={mobile || rightOpen}
          hidden={mobile && view !== 'agent'}
          collapsible={!mobile}
          onToggle={() => setRightOpen((o) => !o)}
          head={
            <DockTabs<SideTab>
              label="Агент и данные"
              active={sideTab}
              onSelect={setSideTab}
              tabs={[
                { key: 'agent', label: 'Агент', count: events.length },
                { key: 'prov', label: 'Источник' },
                { key: 'runs', label: 'Запуски', count: runs.length },
              ]}
            />
          }
        >
          <div role="tabpanel" aria-label="Агент" hidden={sideTab !== 'agent'}>
            <AgentPanel status={status} events={events} tz={tz} synthetic={synthetic} />
          </div>
          <div role="tabpanel" aria-label="Источник прогноза" hidden={sideTab !== 'prov'}>
            <ProvenanceCard metadata={forecast?.metadata ?? null} status={status} issueTime={current?.request.issue_time ?? null} tz={tz} />
          </div>
          <div role="tabpanel" aria-label="Запуски" hidden={sideTab !== 'runs'}>
            <section className="card" aria-labelledby="runs-h">
              <h2 id="runs-h">
                Запуски <small>сервер + этот браузер</small>
              </h2>
              {runs.length === 0 ? (
                <p className="unknown">Запусков ещё не было.</p>
              ) : (
                <ul className="runs">
                  {runs.map((r) => (
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
          </div>
        </Dock>

        {overlayOpen && (
          <button
            type="button"
            className="ws-scrim"
            aria-label="Закрыть боковые панели"
            onClick={() => {
              if (leftOverlay) setLeftOpen(false)
              if (rightOverlay) setRightOpen(false)
            }}
          />
        )}
      </div>

      <footer className="statusbar" title={FOOTNOTE}>
        <span>
          Мощность — нормализованная, как в SCADA (номинал неизвестен), <b>не МВт</b>
        </span>
        <span>Погода: ECMWF, одна ячейка, только прогнозы, вышедшие до выпуска (время доступности — допущение)</span>
        <span>Open-Meteo, CC BY 4.0</span>
        <span className="statusbar-keys" aria-hidden>
          <kbd>1</kbd>–<kbd>4</kbd> разделы · <kbd>[</kbd> <kbd>]</kbd> панели
        </span>
      </footer>
    </div>
  )
}
