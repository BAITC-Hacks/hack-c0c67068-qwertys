import { useState } from 'react';
import { formatTime } from './domain';
import type { ForecastRow } from './types';

export default function Chart({ rows, offset, example }: { rows: ForecastRow[]; offset: string; example: boolean }) {
  const [active, setActive] = useState<number | null>(null);
  const width = 920, height = 270, left = 48, right = 16, top = 24, bottom = 38;
  const plotW = width - left - right, plotH = height - top - bottom;
  const turbines = [...new Set(rows.map(r => r.turbine_id))].sort();
  const times = [...new Set(rows.map(r => Date.parse(r.valid_time)))].sort((a, b) => a - b);
  const start = times[0] ?? 0, end = times.at(-1) ?? 1;
  const x = (time: number) => left + (time - start) / Math.max(3600000, end - start) * plotW;
  const y = (value: number) => top + (1 - value) * plotH;
  const selected = active === null ? undefined : times[Math.min(active, times.length - 1)];
  const colors = ['#29785d', '#7598c4'];
  const segments = (id: string) => {
    const series = rows.filter(r => r.turbine_id === id).sort((a, b) => Date.parse(a.valid_time) - Date.parse(b.valid_time));
    const paths: string[] = []; let path = ''; let last = 0;
    for (const row of series) {
      const time = Date.parse(row.valid_time);
      if (row.y_pred === null || (last && time - last > 3600000)) { if (path) paths.push(path); path = ''; }
      if (row.y_pred !== null) path += `${path ? ' L' : 'M'}${x(time)},${y(row.y_pred)}`;
      last = time;
    }
    if (path) paths.push(path);
    return paths;
  };
  if (!rows.length) return <div className="chart-empty"><div className="empty-curve">⌁</div><h3>Здесь появится прогноз</h3><p>Выберите момент выпуска и запустите расчёт.<br />Почасовые значения придут из модели.</p></div>;
  return <div className="chart-wrap">
    <div className="chart-legend"><span className="axis-caption">Нормализованная мощность · 0–1</span>{turbines.map((id, i) => <span key={id}><i style={{ background: colors[i % colors.length] }} />Турбина {id}</span>)}</div>
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${example ? 'Синтетический пример' : 'Прогноз'} почасовой нормализованной мощности. Точные значения доступны в таблице ниже.`}>
      <defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#5ca981" stopOpacity=".15"/><stop offset="100%" stopColor="#5ca981" stopOpacity=".015"/></linearGradient></defs>
      {[0, .25, .5, .75, 1].map(v => <g key={v}><line x1={left} x2={width - right} y1={y(v)} y2={y(v)} stroke="#e9eeeb" strokeDasharray={v === 0 ? '0' : '4 5'}/><text x={left - 12} y={y(v) + 4} textAnchor="end" className="chart-text">{v.toFixed(v % 1 ? 2 : 1)}</text></g>)}
      {times.filter((_, i) => i % Math.max(1, Math.ceil(times.length / 7)) === 0 || i === times.length - 1).map(t => <text key={t} x={x(t)} y={height - 10} textAnchor="middle" className="chart-text">{formatTime(new Date(t).toISOString(), offset)}</text>)}
      {turbines.map((id, i) => <g key={id}>{segments(id).map((path, j) => <path key={j} d={path} fill="none" stroke={colors[i % colors.length]} strokeWidth="2.7" strokeLinecap="round" strokeLinejoin="round" />)}</g>)}
      {selected !== undefined && <line x1={x(selected)} x2={x(selected)} y1={top} y2={height - bottom} stroke="#879b8e" strokeDasharray="4 4"/>}
      <rect x={left} y={top} width={plotW} height={plotH} fill="transparent" onMouseMove={event => { const rect = event.currentTarget.getBoundingClientRect(); const ratio = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)); setActive(Math.round(ratio * (times.length - 1))); }} onMouseLeave={() => setActive(null)} />
    </svg>
    <div className="chart-detail" aria-live="polite">{selected !== undefined ? <><b>{formatTime(new Date(selected).toISOString(), offset, true)}</b>{turbines.map(id => { const row = rows.find(r => r.turbine_id === id && Date.parse(r.valid_time) === selected); return <span key={id}>Турбина {id}: <strong>{row?.y_pred?.toFixed(3) ?? 'Нет данных'}</strong></span>; })}</> : <span>Наведите на график для просмотра значений · время UTC{offset}</span>}</div>
  </div>;
}
