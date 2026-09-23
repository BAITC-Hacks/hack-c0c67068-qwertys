import type { ForecastRow, TurbineId } from '../api/types'
import { fmtDayHour, type DisplayTz } from '../lib/time'
import { TURBINE_LABEL } from './ForecastChart'

interface Props {
  rows: ForecastRow[]
  turbines: TurbineId[]
  tz: DisplayTz
}

const mean = (xs: number[]) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null)
const f3 = (v: number | null) => (v == null ? '—' : v.toFixed(3))

/** Stat tiles computed only from the returned rows — no thresholds, no invented units. */
export function KpiStrip({ rows, turbines, tz }: Props) {
  return (
    <div className="kpis" role="list" aria-label="Сводка прогноза">
      {turbines.map((t) => {
        const r = rows.filter((x) => x.turbine_id === t && x.y_pred != null).sort((a, b) => a.lead_hours - b.lead_hours)
        const v = (lo: number, hi: number) => r.filter((x) => x.lead_hours >= lo && x.lead_hours <= hi).map((x) => x.y_pred as number)
        const peak = r.reduce<ForecastRow | null>((m, x) => (m == null || (x.y_pred as number) > (m.y_pred as number) ? x : m), null)
        let ramp: { d: number; at: string } | null = null
        for (let i = 1; i < r.length; i++) {
          if (r[i].lead_hours !== r[i - 1].lead_hours + 1) continue
          const d = (r[i].y_pred as number) - (r[i - 1].y_pred as number)
          if (!ramp || Math.abs(d) > Math.abs(ramp.d)) ramp = { d, at: r[i].valid_time }
        }
        const m2 = v(25, 48)
        return (
          <div key={t} className={`kpi ${t}`} role="listitem">
            <div className="kpi-title">
              <span className="kpi-dot" aria-hidden />
              {TURBINE_LABEL[t]}
            </div>
            <div className="kpi-grid">
              <div>
                <span>среднее 1–24 ч</span>
                <b>{f3(mean(v(1, 24)))}</b>
              </div>
              {m2.length > 0 && (
                <div>
                  <span>среднее 25–48 ч</span>
                  <b>{f3(mean(m2))}</b>
                </div>
              )}
              <div>
                <span>пик</span>
                <b>{f3(peak?.y_pred ?? null)}</b>
                {peak && <small>{fmtDayHour(Date.parse(peak.valid_time), tz)}</small>}
              </div>
              <div>
                <span>макс. изменение за час</span>
                <b>{ramp ? `${ramp.d >= 0 ? '+' : '−'}${Math.abs(ramp.d).toFixed(3)}` : '—'}</b>
                {ramp && <small>{fmtDayHour(Date.parse(ramp.at), tz)}</small>}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
