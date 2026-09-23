import { useEffect, useRef, useState } from 'react';
import { runForecast } from './api';
import Chart from './Chart';
import { formatTime, makeCsv, timestamp } from './domain';
import { exampleResult } from './example';
import type { ForecastRequest, Horizon, Mode, RunResult, RunStatus } from './types';

function Icon({ name, size = 20 }: { name: string; size?: number }) {
  const paths: Record<string, React.ReactNode> = {
    wind: <><path d="M3 8h12a3 3 0 1 0-3-3M3 12h16a3 3 0 1 1-3 3M3 16h5a3 3 0 1 1-3 3"/></>,
    chart: <><path d="M4 4v16h16M8 14l4-5 4 3 5-7"/></>,
    clock: <><circle cx="12" cy="12" r="8"/><path d="M12 7v5l3 2"/></>,
    download: <><path d="M12 3v12m-4-4 4 4 4-4M4 16v5h16v-5"/></>,
    arrow: <path d="M5 12h14m-5-5 5 5-5 5"/>,
    check: <path d="m5 12 4 4L19 6"/>,
    info: <><circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v1"/></>,
    turbine: <><path d="M12 12v10M12 10V1M12 10 3 16M12 10l9 6"/><circle cx="12" cy="10" r="1.5"/></>,
    refresh: <><path d="M20 7v5h-5M4 17v-5h5"/><path d="M6 7a7 7 0 0 1 12-2l2 3M4 16l2 3a7 7 0 0 0 12-2"/></>,
    list: <><path d="M8 6h12M8 12h12M8 18h12M3 6h1m-1 6h1m-1 6h1"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] ?? paths.info}</svg>;
}

const stateLabels: Record<string, string> = { queued: 'В очереди', pending: 'В очереди', running: 'Идёт расчёт', completed: 'Расчёт завершён', success: 'Расчёт завершён', succeeded: 'Расчёт завершён', done: 'Расчёт завершён', failed: 'Ошибка расчёта', error: 'Ошибка расчёта', example: 'Тестовый пример' };

export default function App() {
  const [issue, setIssue] = useState('2026-01-31T23:00');
  const [offset, setOffset] = useState('+06:00');
  const [turbine, setTurbine] = useState('both');
  const [horizon, setHorizon] = useState<Horizon>(48);
  const [version, setVersion] = useState('latest');
  const [mode, setMode] = useState<Mode>('api');
  const [result, setResult] = useState<RunResult | null>(null);
  const [history, setHistory] = useState<RunResult[]>([]);
  const [status, setStatus] = useState<RunStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [tab, setTab] = useState<'chart' | 'table'>('chart');
  const [tableTurbine, setTableTurbine] = useState('all');
  const abort = useRef<AbortController | null>(null);
  const requestNumber = useRef(0);
  useEffect(() => () => abort.current?.abort(), []);

  async function launch() {
    const number = ++requestNumber.current;
    abort.current?.abort();
    const controller = new AbortController(); abort.current = controller;
    const issueTime = `${issue}:00${offset}`;
    if (!timestamp(issueTime)) { setError('Укажите корректный момент выпуска и часовой пояс.'); return; }
    if (!version.trim()) { setError('Укажите версию входных данных.'); return; }
    const request: ForecastRequest = { issue_time: issueTime, turbine_ids: turbine === 'both' ? ['1', '2'] : [turbine], horizon_hours: horizon, input_version: version.trim() };
    setError(''); setStatus(null); setBusy(true);
    try {
      const next = mode === 'example' ? exampleResult(request) : await runForecast(request, controller.signal, s => { if (number === requestNumber.current) setStatus(s); });
      if (number !== requestNumber.current) return;
      setResult(next); setStatus(next.status); setTableTurbine('all');
      setHistory(old => [next, ...old.filter(r => r.status.run_id !== next.status.run_id)].slice(0, 8));
    } catch (e) {
      if (number === requestNumber.current && !controller.signal.aborted) setError(e instanceof Error ? e.message : 'Не удалось выполнить расчёт.');
    } finally { if (number === requestNumber.current) setBusy(false); }
  }

  function cancel() { requestNumber.current++; abort.current?.abort(); setBusy(false); setError('Ожидание остановлено. Уже созданный расчёт может продолжаться на сервере.'); }
  function exportCsv() {
    if (!result) return;
    const url = URL.createObjectURL(new Blob([makeCsv(result)], { type: 'text/csv;charset=utf-8;' }));
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = `${result.mode === 'example' ? 'SYNTHETIC-' : ''}forecast-${result.status.run_id.replace(/[^a-zA-Z0-9_-]/g, '_')}.csv`; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  const rows = result?.rows ?? [];
  const valid = rows.filter(r => r.y_pred !== null);
  const expected = result ? result.request.horizon_hours * result.request.turbine_ids.length : horizon * (turbine === 'both' ? 2 : 1);
  const maximum = valid.length ? Math.max(...valid.map(r => r.y_pred!)) : null;
  const resultOffset = result?.request.issue_time.slice(-6) ?? offset;
  const visibleRows = rows.filter(r => tableTurbine === 'all' || r.turbine_id === tableTurbine).sort((a, b) => Date.parse(a.valid_time) - Date.parse(b.valid_time) || a.turbine_id.localeCompare(b.turbine_id));
  const weather = result?.status.weather;
  const isExample = result?.mode === 'example';

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="#forecast" aria-label="QwertyS — прогноз ВЭС"><span className="brand-icon"><Icon name="turbine" size={25}/></span><span>QwertyS<small>WIND INTELLIGENCE</small></span></a>
      <div className="nav-label">РАБОЧАЯ ОБЛАСТЬ</div>
      <nav><a className="nav-link active" href="#forecast"><Icon name="chart"/>Прогноз мощности<span>↗</span></a><a className="nav-link" href="#journal"><Icon name="list"/>Журнал расчёта</a><a className="nav-link" href="#source"><Icon name="info"/>Источники данных</a></nav>
      <div className="site-card"><span className="site-eyebrow">ПЛОЩАДКА</span><div className="site-title">Шелекский коридор</div><p>Алматинская область</p><div className="turbine-art"><Icon name="turbine" size={68}/><Icon name="turbine" size={48}/><div/></div><span className="site-count">2 турбины · почасовой прогноз</span></div>
      <div className="sidebar-footer"><span className="avatar">QS</span><span>HackAlem AI<small>Команда QwertyS · 2026</small></span></div>
    </aside>

    <div className="workspace">
      <header className="topbar"><div><span className="breadcrumb">Ветроэлектростанция</span><span className="slash">/</span> Прогноз</div><span className="top-tag"><span className="dot"/>Исторический сценарий</span></header>
      <main id="forecast">
        <div className="page-heading"><div><div className="eyebrow">ПЛАНИРОВАНИЕ ВЫРАБОТКИ</div><h1>Ветер в данных.<br className="mobile-break"/> Мощность в прогнозе.</h1><p>Почасовой прогноз двух турбин на следующие 24–48 часов.</p></div><span className="period-tag"><Icon name="clock"/>Февраль 2026</span></div>

        <section className="panel controls" aria-labelledby="settings-title"><div className="section-heading"><div><span className="section-index">01</span><h2 id="settings-title">Параметры прогноза</h2></div><span className="muted small">Погода, доступная на момент выпуска</span></div>
          <form onSubmit={event => { event.preventDefault(); void launch(); }}>
            <div className="form-grid"><label>Момент выпуска<input type="datetime-local" value={issue} onChange={e => setIssue(e.target.value)} required disabled={busy}/></label><label>Часовой пояс<select value={offset} onChange={e => setOffset(e.target.value)} disabled={busy}><option value="+06:00">UTC+6 · гипотеза SCADA</option><option value="+05:00">UTC+5</option><option value="+00:00">UTC</option></select></label><label>Турбины<select value={turbine} onChange={e => setTurbine(e.target.value)} disabled={busy}><option value="both">Обе турбины</option><option value="1">Турбина 1</option><option value="2">Турбина 2</option></select></label><fieldset className="horizon"><legend>Горизонт</legend><div className="segmented">{([24, 48] as const).map(h => <button type="button" key={h} aria-pressed={horizon === h} disabled={busy} className={horizon === h ? 'selected' : ''} onClick={() => setHorizon(h)}>{h} ч</button>)}</div></fieldset><button className="primary launch" type="submit" disabled={busy}>{busy ? <><span className="spinner"/>Считаем…</> : <><Icon name={result ? 'refresh' : 'arrow'}/>{result ? 'Пересчитать' : 'Рассчитать прогноз'}</>}</button></div>
            <div className="controls-bottom"><span><Icon name="info" size={15}/>Значения мощности нормализованы, без пересчёта в МВт.</span><details><summary>Настройки запуска</summary><div className="advanced"><label>Источник результата<select value={mode} onChange={e => setMode(e.target.value as Mode)} disabled={busy}><option value="api">Расчёт через API</option><option value="example">Синтетический пример интерфейса</option></select></label><label>Версия входных данных<input value={version} maxLength={120} onChange={e => setVersion(e.target.value)} disabled={busy}/></label><p>Изменение версии передаётся серверу для пересчёта. Часовой пояс данных требует подтверждения.</p></div></details></div>
          </form>
        </section>

        {busy && <div className="notice loading" role="status"><span className="spinner"/><div><b>{status ? stateLabels[status.state] ?? status.state : 'Отправляем запрос'}</b><span>{status ? `Запуск ${status.run_id}` : 'Ожидаем ответ сервера'}</span></div><button className="text-button" onClick={cancel}>Остановить ожидание</button></div>}
        {error && <div className="notice error" role="alert"><Icon name="info"/><div><b>{error}</b>{result && <span>Ниже сохранён предыдущий результат: {result.status.run_id}.</span>}</div></div>}
        {result && <div className={`result-banner ${isExample ? 'example' : ''}`}><span><Icon name={isExample ? 'info' : 'check'} size={17}/>{isExample ? 'СИНТЕТИЧЕСКИЙ ПРИМЕР · не прогноз ВЭС' : `Результат API · ${result.status.mode ?? 'режим не указан сервером'}`}</span><span>Выпуск {formatTime(result.request.issue_time, resultOffset, true)} · UTC{resultOffset} · {result.request.horizon_hours} ч</span></div>}

        <div className="metrics"><article className="metric"><div><span>Покрытие прогноза</span><Icon name="clock"/></div><strong>{result ? `${valid.length}` : '—'}<small>{result ? ` / ${expected}` : ' часов'}</small></strong><p>{result ? `${result.request.turbine_ids.length} турб. × ${result.request.horizon_hours} ч${isExample ? ' · пример' : ''}` : 'Ожидаем результат расчёта'}</p></article><article className="metric"><div><span>Максимальная мощность</span><Icon name="wind"/></div><strong>{maximum === null ? '—' : maximum.toFixed(3)}<small> отн. ед.</small></strong><p>{isExample ? 'Синтетическое значение' : 'Среди полученных почасовых значений'}</p></article><article className="metric"><div><span>Погодный источник</span><Icon name="turbine"/></div><strong className="metric-word">{isExample ? 'Нет погоды' : weather?.provider ?? 'Не указан'}</strong><p>{isExample ? 'Пример создан только для UI' : weather?.model ?? 'Источник появится в результате'}</p></article></div>

        <section className="panel forecast-panel" aria-labelledby="chart-title"><div className="section-heading"><div><span className="section-index">02</span><h2 id="chart-title">Почасовая мощность</h2></div><div className="chart-actions"><div className="segmented compact" aria-label="Вид прогноза"><button className={tab === 'chart' ? 'selected' : ''} aria-pressed={tab === 'chart'} onClick={() => setTab('chart')}><Icon name="chart" size={16}/>График</button><button className={tab === 'table' ? 'selected' : ''} aria-pressed={tab === 'table'} onClick={() => setTab('table')}><Icon name="list" size={16}/>Таблица</button></div><button className="outline" disabled={!result} onClick={exportCsv}><Icon name="download" size={16}/>CSV</button></div></div>
          {tab === 'chart' ? <Chart rows={rows} offset={resultOffset} example={Boolean(isExample)}/> : <div className="table-view"><label className="table-filter">Показать<select value={tableTurbine} onChange={e => setTableTurbine(e.target.value)}><option value="all">Все турбины</option>{[...new Set(rows.map(r => r.turbine_id))].map(id => <option key={id} value={id}>Турбина {id}</option>)}</select></label><div className="table-scroll"><table><caption>{isExample ? 'Синтетические значения' : 'Почасовой прогноз'} · UTC{resultOffset} · нормализованная мощность</caption><thead><tr><th>Целевой час</th><th>Турбина</th><th>Горизонт</th><th>Мощность</th><th>Резервный метод</th></tr></thead><tbody>{visibleRows.map(row => <tr key={`${row.turbine_id}-${row.valid_time}`}><td>{formatTime(row.valid_time, resultOffset, true)}</td><td><span className={`turbine-dot t${row.turbine_id}`}/>Турбина {row.turbine_id}</td><td>+{row.lead_hours} ч</td><td className="numeric">{row.y_pred?.toFixed(4) ?? 'Нет данных'}</td><td>{row.fallback_status ?? '—'}</td></tr>)}</tbody></table>{!rows.length && <p className="table-empty">Запустите расчёт, чтобы получить почасовые значения.</p>}</div></div>}
          <div className="panel-footnote"><Icon name="info" size={15}/>Фактические данные за февраль не предоставлены. Ошибка прогноза за этот период не рассчитывается.</div>
        </section>

        {!!result?.warnings.length && <div className="warnings" role="status">{result.warnings.map(warning => <p key={warning}><Icon name="info" size={16}/>{warning}</p>)}</div>}
        <div className="lower-grid"><section className="panel" id="journal" aria-labelledby="journal-title"><div className="section-heading"><div><span className="section-index">03</span><h2 id="journal-title">Журнал расчёта</h2></div><span className="badge">{result?.events.length ?? 0} событий</span></div>{result?.events.length ? <ol className="events">{result.events.map((event, i) => <li key={i}><span className="event-marker">{i + 1}</span><div><h3>{event.tool_name}</h3><p>{event.state_transition}</p>{event.safe_input_summary && <p>{event.safe_input_summary}</p>}{event.result_reference && <code>{event.result_reference}</code>}</div><time>{formatTime(event.timestamp, resultOffset)}</time></li>)}</ol> : <div className="empty-journal"><Icon name="list" size={28}/><p>{isExample ? 'В тестовом примере нет вызовов агента.' : 'Действия появятся после получения журнала API.'}</p><span>Загрузка погоды → подготовка → прогноз → анализ</span></div>}</section>
          <section className="panel" id="source" aria-labelledby="source-title"><div className="section-heading"><div><span className="section-index">04</span><h2 id="source-title">Происхождение результата</h2></div></div><dl className="source-list"><div><dt>Запуск</dt><dd>{result?.status.run_id ?? 'Ещё не создан'}</dd></div><div><dt>Версия модели</dt><dd>{result?.status.model_version ?? rows[0]?.model_version ?? 'Не указана'}</dd></div><div><dt>Погодная модель</dt><dd>{weather?.model ?? 'Не указана'}</dd></div><div><dt>Выпуск погоды</dt><dd>{formatTime(weather?.run_time, resultOffset, true)}</dd></div><div><dt>Доступен с</dt><dd>{formatTime(weather?.available_at, resultOffset, true)}</dd></div><div><dt>Версия входов</dt><dd>{result?.status.input_version ?? result?.request.input_version ?? '—'}</dd></div><div><dt>Источник</dt><dd>{weather?.source_reference ?? rows[0]?.weather_reference ?? 'Не указан'}</dd></div></dl><p className="source-note">Время показано в UTC{resultOffset}. Источник должен быть доступен не позже момента выпуска прогноза.</p></section></div>
        {history.length > 1 && <section className="run-history"><h2>Результаты этой сессии</h2>{history.map(run => <button key={run.status.run_id} onClick={() => { setResult(run); setTableTurbine('all'); }} className={result?.status.run_id === run.status.run_id ? 'selected' : ''}>{run.mode === 'example' ? 'Пример UI' : run.status.run_id} · {run.request.horizon_hours} ч</button>)}</section>}
        <footer className="page-footer"><span>QwertyS · HackAlem AI 2026</span><span>Архивная погода. Проверяемый расчёт.</span></footer>
      </main>
    </div>
  </div>;
}
