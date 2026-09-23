// Display helpers. Kazakhstan civil time since 2024-03-01 is UTC+5 (single zone).
// SCADA clock is a separate question (inferred fixed UTC+6) and handled by the backend.
export type DisplayTz = 'local' | 'utc'
export const LOCAL_OFFSET_H = 5

function shift(ms: number, tz: DisplayTz): Date {
  return new Date(ms + (tz === 'local' ? LOCAL_OFFSET_H * 3600_000 : 0))
}
const p2 = (n: number) => String(n).padStart(2, '0')

export function fmtHour(ms: number, tz: DisplayTz): string {
  const d = shift(ms, tz)
  // show the date at midnight so multi-day axes stay readable
  return d.getUTCHours() === 0 ? `${p2(d.getUTCDate())}.${p2(d.getUTCMonth() + 1)}` : `${p2(d.getUTCHours())}:00`
}
export function fmtDayHour(ms: number, tz: DisplayTz): string {
  const d = shift(ms, tz)
  return `${p2(d.getUTCDate())}.${p2(d.getUTCMonth() + 1)} ${p2(d.getUTCHours())}:${p2(d.getUTCMinutes())}`
}
export function fmtIso(iso: string | null | undefined, tz: DisplayTz): string | null {
  if (!iso) return null
  const ms = Date.parse(iso)
  if (Number.isNaN(ms)) return iso
  return `${fmtDayHour(ms, tz)} ${tzLabel(tz)}`
}
export function tzLabel(tz: DisplayTz): string {
  return tz === 'local' ? `UTC+${LOCAL_OFFSET_H}` : 'UTC'
}

/** Issue dates of the case replay: 2026-01-31 … 2026-02-28. */
export function replayDates(): string[] {
  const out: string[] = []
  for (let d = Date.UTC(2026, 0, 31); d <= Date.UTC(2026, 1, 28); d += 86400_000) {
    out.push(new Date(d).toISOString().slice(0, 10))
  }
  return out
}

/** Build RFC3339 issue_time from a local (UTC+5) date + hour. */
export function issueTimeFromLocal(date: string, hour: number): string {
  return `${date}T${p2(hour)}:00:00+05:00`
}

/** Local (UTC+5) date "YYYY-MM-DD" and hour of an RFC3339 timestamp. */
export function localDateHour(iso: string): { date: string; hour: number } {
  const d = new Date(Date.parse(iso) + LOCAL_OFFSET_H * 3600_000)
  return { date: d.toISOString().slice(0, 10), hour: d.getUTCHours() }
}
