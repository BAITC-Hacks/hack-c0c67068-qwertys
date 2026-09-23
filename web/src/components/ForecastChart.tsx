import {
  CartesianGrid,
  Line,
  LineChart,
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
const COLOR: Record<TurbineId, string> = { turbine_1: 'var(--t1)', turbine_2: 'var(--t2)' }

interface Props {
  rows: ForecastRow[]
  previous?: ForecastRow[] | null
  turbines: TurbineId[]
  issueTime: string | null
  tz: DisplayTz
  synthetic: boolean
}

type Point = { t: number; lead: number } & Partial<Record<string, number>>

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

export function ForecastChart({ rows, previous, turbines, issueTime, tz, synthetic }: Props) {
  if (!rows.length) {
    return (
      <div className="chart-wrap">
        <div className="empty">Прогноза пока нет. Выберите дату выпуска и запустите агента.</div>
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
      <div className="chart-wrap" role="img" aria-label="Почасовой прогноз нормализованной мощности">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 16, bottom: 4, left: 0 }}>
            <CartesianGrid stroke="var(--grid)" vertical={false} />
            {split != null && last != null && last > split && (
              <ReferenceArea x1={split} x2={last} fill="var(--surface-2)" fillOpacity={0.9} ifOverflow="hidden" />
            )}
            <XAxis
              dataKey="t"
              type="number"
              scale="time"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(v: number) => fmtHour(v, tz)}
              stroke="var(--axis)"
              tick={{ fill: 'var(--muted)', fontSize: 11 }}
              minTickGap={24}
            />
            <YAxis
              domain={[0, 1]}
              ticks={[0, 0.25, 0.5, 0.75, 1]}
              stroke="var(--axis)"
              tick={{ fill: 'var(--muted)', fontSize: 11 }}
              width={40}
            />
            {split != null && (
              <ReferenceLine x={split} stroke="var(--axis)" strokeDasharray="3 3" label={{ value: '24 ч', position: 'insideTopRight', fill: 'var(--muted)', fontSize: 11 }} />
            )}
            <Tooltip
              labelFormatter={(v) => `${fmtDayHour(Number(v), tz)} ${tzLabel(tz)}`}
              formatter={(value, name) => [typeof value === 'number' ? value.toFixed(3) : String(value), String(name)]}
              contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: 'var(--ink)' }}
            />
            {turbines.map((t) => (
              <Line key={t} dataKey={t} name={TURBINE_LABEL[t]} stroke={COLOR[t]} strokeWidth={2} dot={false} activeDot={{ r: 4 }} isAnimationActive={false} />
            ))}
            {hasPrev &&
              turbines.map((t) => (
                <Line key={`prev_${t}`} dataKey={`prev_${t}`} name={`${TURBINE_LABEL[t]} — пред. версия`} stroke={COLOR[t]} strokeWidth={1.5} strokeDasharray="5 4" strokeOpacity={0.75} dot={false} isAnimationActive={false} connectNulls={false} />
              ))}
          </LineChart>
        </ResponsiveContainer>
        {synthetic && <div className="watermark">СИНТЕТИКА</div>}
      </div>
      <div className="legend-note">
        {turbines.map((t) => (
          <span key={t}><span className="swatch" style={{ borderColor: COLOR[t] }} />{TURBINE_LABEL[t]}</span>
        ))}
        {hasPrev && <span><span className="swatch dashed" style={{ borderColor: 'var(--ink-2)' }} />предыдущая версия (общие часы)</span>}
        <span>Ось Y: нормализованная мощность (0–1), не МВт · время {tzLabel(tz)} · серая зона: упреждение 25–48 ч</span>
      </div>
    </>
  )
}
