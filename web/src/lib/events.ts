// Agent event summaries arrive either as plain text or as a JSON object string (C2 tools).
// Parse without inventing anything: show keys/values exactly as returned.

export interface ParsedSummary {
  text: string
  fields: [string, string][] | null
}

const LABEL: Record<string, string> = {
  hours: 'часов',
  rows: 'строк',
  run_time: 'прогон',
  provenance_status: 'происхождение',
  availability_basis: 'доступность',
  model_version: 'модель',
  training_end_exclusive: 'обучение до',
  future_scada_lags: 'лаги SCADA из будущего',
  unit: 'единица',
  min: 'мин',
  max: 'макс',
  coverage: 'покрытие',
  warnings: 'предупреждения',
  export_id: 'export',
  formats: 'форматы',
  status: 'статус',
  turbines: 'турбины',
}

function fmtValue(v: unknown): string {
  if (v == null) return '—'
  if (typeof v === 'number') return Number.isInteger(v) ? String(v) : v.toFixed(3)
  if (typeof v === 'boolean') return v ? 'да' : 'нет'
  if (Array.isArray(v)) return v.map(fmtValue).join('; ')
  if (typeof v === 'object') return JSON.stringify(v)
  const s = String(v)
  // ISO timestamps → compact UTC
  return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(s) ? `${s.slice(8, 10)}.${s.slice(5, 7)} ${s.slice(11, 16)}Z` : s
}

export function parseSummary(summary: string): ParsedSummary {
  const t = summary.trim()
  if (!t.startsWith('{')) return { text: summary, fields: null }
  try {
    const obj = JSON.parse(t) as Record<string, unknown>
    const fields = Object.entries(obj).map(([k, v]) => [LABEL[k] ?? k, fmtValue(v)] as [string, string])
    const text = fields
      .filter(([k]) => k !== 'предупреждения')
      .slice(0, 4)
      .map(([k, v]) => `${k}: ${v}`)
      .join(' · ')
    return { text: text || summary, fields }
  } catch {
    return { text: summary, fields: null }
  }
}
