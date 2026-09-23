import type { ForecastRow, TurbineId } from '../api/types'
import { buildPoints, TURBINE_LABEL } from './ForecastChart'
import { fmtDayHour, tzLabel, type DisplayTz } from '../lib/time'

interface Props {
  rows: ForecastRow[]
  previous?: ForecastRow[] | null
  turbines: TurbineId[]
  tz: DisplayTz
}

const fmt = (v: number | undefined) => (v == null ? '—' : v.toFixed(3))

export function ForecastTable({ rows, previous, turbines, tz }: Props) {
  if (!rows.length) return null
  const data = buildPoints(rows, previous)
  const hasPrev = !!previous?.length
  return (
    <div className="table-scroll">
      <table>
        <caption className="sr-only">Почасовой прогноз нормализованной мощности</caption>
        <thead>
          <tr>
            <th scope="col">Время ({tzLabel(tz)})</th>
            <th scope="col">Упр., ч</th>
            {turbines.map((t) => (
              <th key={t} scope="col">{TURBINE_LABEL[t]}</th>
            ))}
            {hasPrev && turbines.map((t) => <th key={`d_${t}`} scope="col">Δ {TURBINE_LABEL[t]}</th>)}
          </tr>
        </thead>
        <tbody>
          {data.map((p, i) => (
            <tr key={p.t} className={i > 0 && p.lead === 25 ? 'day-break' : undefined}>
              <td>{fmtDayHour(p.t, tz)}</td>
              <td>{p.lead}</td>
              {turbines.map((t) => (
                <td key={t}>{fmt(p[t])}</td>
              ))}
              {hasPrev &&
                turbines.map((t) => {
                  const a = p[t]
                  const b = p[`prev_${t}`]
                  return <td key={`d_${t}`}>{a != null && b != null ? (a - b >= 0 ? '+' : '') + (a - b).toFixed(3) : '—'}</td>
                })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
