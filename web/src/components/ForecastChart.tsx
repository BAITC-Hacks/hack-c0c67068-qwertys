import {
  Area,
  Brush,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { ForecastRow, TurbineId } from '../api/types'
import { fmtDayHour, fmtHour, tzLabel, type DisplayTz } from '../lib/time'

export const TURBINE_LABEL: Record<TurbineId, string> = { turbine_1: 'Турбина 1', turbine_2: 'Турбина 2' }
export const COLOR: Record<TurbineId, string> = { turbine_1: 'var(--t1)', turbine_2: 'var(--t2)' }

type TipItem = { dataKey?: unknown; name?: unknown; value?: unknown; color?: string; type?: string; payload?: { lead?: number } }

/** Shared chart tooltip: time (+ lead when known), one row per series; dashed marker for the previous version. */
export function ChartTip({ active, payload, label, tz }: { active?: boolean; payload?: readonly unknown[]; label?: unknown; tz: DisplayTz }) {
  // drop the decorative gradient areas (tooltipType none / unnamed)
  const items = ((payload ?? []) as readonly TipItem[]).filter((p) => p.type !== 'none' && String(p.name) !== String(p.dataKey))
  if (!active || !items.length) return null
  const lead = items[0]?.payload?.lead
  return (
    <div className="ttip">
      <div className="ttip-h">
        <span>
          {fmtDayHour(Number(label), tz)} {tzLabel(tz)}
        </span>
        {lead != null && <b>+{lead} ч</b>}
      </div>
      {items.map((p) => {
        const key = String(p.dataKey)
        return (
          <div key={key} className="ttip-row">
            <i className={key.startsWith('prev_') ? 'dashed' : undefined} style={{ background: p.color, borderColor: p.color }} />
            <span>{String(p.name)}</span>
            <b>{typeof p.value === 'number' ? p.value.toFixed(3) : '—'}</b>
          </div>
        )
      })}
    </div>
  )
}

interface Props {
  rows: ForecastRow[]
  previous?: ForecastRow[] | null
  turbines: TurbineId[]
  issueTime: string | null
  tz: DisplayTz
  synthetic: boolean
  loadingStage?: string | null
}

type Point = { t: number; lead: number } & Partial<Record<string, number | null>>

export function buildPoints(rows: ForecastRow[], previous?: ForecastRow[] | null): Point[] {
  const byT = new Map<number, Point>()
  for (const r of rows) {
    const t = Date.parse(r.valid_time)
    const p = byT.get(t) ?? { t, lead: r.lead_hours }
    p[r.turbine_id] = r.y_pred
    byT.set(t, p)
  }
  for (const r of previous ?? []) {
    const t = Date.parse(r.valid_time)
    const p = byT.get(t)
    if (p) p[`prev_${r.turbine_id}`] = r.y_pred // only common valid hours
  }
  return [...byT.values()].sort((a, b) => a.t - b.t)
}

const STAGE_RU: Record<string, string> = { weather: 'получение погоды', prepare: 'загрузка и проверка модели', forecast: 'расчёт модели', validate: 'анализ результата', export: 'экспорт' }

export function ForecastChart({ rows, previous, turbines, issueTime, tz, synthetic, loadingStage }: Props) {
  if (!rows.length) {
    return (
      <div className="chart-wrap">
        {loadingStage !== undefined && loadingStage !== null ? (
          <div className="skeleton" aria-busy="true" aria-live="polite">
            <div className="sk-lines" aria-hidden>
              <span />
              <span />
              <span />
            </div>
            <p>Агент работает: {STAGE_RU[loadingStage] ?? (loadingStage || 'в очереди')}…</p>
          </div>
        ) : (
          <div className="empty">Прогноза пока нет. Выберите дату выпуска и запустите агента.</div>
        )}
      </div>
    )
  }
  const data = buildPoints(rows, previous)
  const issueMs = issueTime ? Date.parse(issueTime) : null
  const split = issueMs != null ? issueMs + 24 * 3600_000 : null
  const last = data[data.length - 1]?.t
  const hasPrev = !!previous?.length

  return (
    <>
      <div className="chart-wrap" role="figure" aria-label="Почасовой прогноз нормализованной мощности; те же данные — в таблице ниже">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 16, bottom: 4, left: 0 }}>
            <defs>
              {/* faint fade to baseline only — not an uncertainty band (no quantiles exist) */}
              {turbines.map((t) => (
                <linearGradient key={t} id={`fill-${t}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" style={{ stopColor: COLOR[t], stopOpacity: turbines.length > 1 ? 0.1 : 0.15 }} />
                  <stop offset="100%" style={{ stopColor: COLOR[t], stopOpacity: 0 }} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid stroke="var(--grid)" strokeDasharray="2 4" vertical={false} />
            {split != null && last != null && last > split && (
              <ReferenceArea x1={split} x2={last} fill="var(--surface-2)" fillOpacity={0.75} ifOverflow="hidden" />
            )}
            <XAxis
              dataKey="t"
              type="number"
              scale="time"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(v: number) => fmtHour(v, tz)}
              stroke="var(--axis)"
              tickLine={false}
              tick={{ fill: 'var(--muted)', fontSize: 11 }}
              minTickGap={24}
            />
            <YAxis
              domain={[0, (max: number) => Math.max(1, Math.ceil(max * 10) / 10)]}
              tickCount={5}
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'var(--muted)', fontSize: 11 }}
              width={40}
            />
            {split != null && (
              <ReferenceLine x={split} stroke="var(--axis)" strokeWidth={1} strokeDasharray="1 3" label={{ value: '24 ч →', position: 'insideTopLeft', fill: 'var(--muted)', fontSize: 11 }} />
            )}
            <Tooltip
              content={(p) => <ChartTip active={p.active} payload={p.payload} label={p.label} tz={tz} />}
              cursor={{ stroke: 'var(--ink-2)', strokeWidth: 1, strokeDasharray: '2 3' }}
            />
            {turbines.map((t) => (
              <Area key={`area_${t}`} dataKey={t} fill={`url(#fill-${t})`} stroke="none" tooltipType="none" activeDot={false} isAnimationActive={false} connectNulls={false} />
            ))}
            {turbines.map((t) => (
              <Line key={t} dataKey={t} name={TURBINE_LABEL[t]} stroke={COLOR[t]} strokeWidth={2.25} dot={false} activeDot={{ r: 4.5, strokeWidth: 2, stroke: 'var(--surface)' }} isAnimationActive={false} connectNulls={false} />
            ))}
            {hasPrev &&
              turbines.map((t) => (
                <Line key={`prev_${t}`} dataKey={`prev_${t}`} name={`${TURBINE_LABEL[t]} — пред. версия`} stroke={COLOR[t]} strokeWidth={1.5} strokeDasharray="5 4" strokeOpacity={0.75} dot={false} isAnimationActive={false} connectNulls={false} />
              ))}
            {data.length > 12 && (
              <Brush dataKey="t" height={22} travellerWidth={8} stroke="var(--muted)" fill="var(--surface-2)" tickFormatter={(v: number) => fmtHour(v, tz)} />
            )}
          </ComposedChart>
        </ResponsiveContainer>
        {synthetic && <div className="watermark">СИНТЕТИКА</div>}
      </div>
      <div className="legend-note">
        {turbines.map((t) => (
          <span key={t}><span className="swatch" style={{ borderColor: COLOR[t] }} />{TURBINE_LABEL[t]}</span>
        ))}
        {hasPrev && <span><span className="swatch dashed" style={{ borderColor: 'var(--ink-2)' }} />предыдущая версия (общие часы)</span>}
        <span>Ось Y: нормализованная мощность (как в SCADA), не МВт · время {tzLabel(tz)} · серая зона: упреждение 25–48 ч · ползунок внизу — масштаб</span>
      </div>
    </>
  )
}
