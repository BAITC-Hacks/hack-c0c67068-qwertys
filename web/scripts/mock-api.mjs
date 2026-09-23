// DEV-ONLY mock of API_CONTRACT_V1 for exercising UI states (queued→running→completed,
// failures, events). Values are fake and every response says model_version "MOCK".
// Never use for demos or results.  Run: node web/scripts/mock-api.mjs  (port 8010, not the real 8000)
// UI against mock: VITE_API_TARGET=http://127.0.0.1:8010 npm run dev
import http from 'node:http'

const runs = new Map()
const STAGES = ['weather', 'prepare', 'forecast', 'validate', 'export']
let n = 0

function json(res, code, body) {
  res.writeHead(code, { 'Content-Type': 'application/json' })
  res.end(JSON.stringify(body))
}

function status(r) {
  const age = (Date.now() - r.t0) / 700
  const i = Math.floor(age)
  const failed = r.req.issue_time.startsWith('2026-02-13') // exercise the failure path
  if (failed && i >= 1) return { ...r.base, status: 'failed', stage: 'weather', forecast_available: false, error: { code: 'weather_unavailable', message: 'MOCK: no admissible run', retryable: true } }
  if (i >= STAGES.length) return { ...r.base, status: 'completed', stage: null, forecast_available: true }
  return { ...r.base, status: i === 0 ? 'queued' : 'running', stage: STAGES[Math.max(0, i - 1)], forecast_available: false }
}

http
  .createServer((req, res) => {
    const url = new URL(req.url, 'http://x')
    const p = url.pathname
    if (p === '/api/health') return json(res, 200, { status: 'ok', forecast_ready: true })
    if (p === '/api/runs' && req.method === 'POST') {
      let body = ''
      req.on('data', (c) => (body += c))
      req.on('end', () => {
        const r = JSON.parse(body)
        const id = `mock-${++n}`
        const rec = { req: r, t0: Date.now(), seed: n, base: { run_id: id, mode: 'deterministic', warnings: ['MOCK backend — not a forecast'], error: null } }
        runs.set(id, rec)
        json(res, 202, status(rec))
      })
      return
    }
    const m = p.match(/^\/api\/runs\/([^/]+)(\/(forecast|events|export\.csv))?$/)
    if (!m) return json(res, 404, { error: { code: 'not_found', message: p, retryable: false } })
    const r = runs.get(m[1])
    if (!r) return json(res, 404, { error: { code: 'unknown_run', message: m[1], retryable: false } })
    const s = status(r)
    if (!m[3]) return json(res, 200, s)
    if (m[3] === 'events') {
      const k = s.status === 'completed' ? STAGES.length : STAGES.indexOf(s.stage) + 1
      return json(res, 200, {
        run_id: m[1],
        events: STAGES.slice(0, Math.max(0, k)).map((st, i) => ({ seq: i + 1, timestamp: new Date(r.t0 + i * 700).toISOString(), tool: `mock_${st}`, state: st.toUpperCase(), summary: `MOCK step ${st}` })),
      })
    }
    if (s.status !== 'completed') return json(res, 409, { error: { code: 'not_ready', message: 'result not ready', retryable: true } })
    const issue = Date.parse(r.req.issue_time)
    const rows = []
    for (const t of r.req.turbine_ids)
      for (let lead = 1; lead <= r.req.horizon_hours; lead++)
        rows.push({ turbine_id: t, issue_time: new Date(issue).toISOString(), valid_time: new Date(issue + lead * 3600e3).toISOString(), lead_hours: lead, y_pred: +(0.5 + 0.35 * Math.sin((issue / 3600e3 + lead) / 9 + r.seed * 0.3) * (t === 'turbine_1' ? 1 : 0.9)).toFixed(3) })
    if (m[3] === 'export.csv') {
      res.writeHead(200, { 'Content-Type': 'text/csv' })
      return res.end(['turbine_id,issue_time,valid_time,lead_hours,y_pred', ...rows.map((x) => Object.values(x).join(','))].join('\n'))
    }
    json(res, 200, {
      run_id: m[1],
      unit: 'normalized_power',
      rows,
      metadata: { model_version: 'MOCK', input_version: null, weather_provider: 'mock', weather_model: 'mock', weather_run_time: new Date(issue - 12 * 3600e3).toISOString(), weather_available_at: new Date(issue - 6 * 3600e3).toISOString(), availability_basis: 'inferred_run_plus_6h', scada_timezone: 'UTC+06:00', timezone_status: 'inferred', provenance_status: 'unconfirmed' },
    })
  })
  .listen(8010, '127.0.0.1', () => console.log('MOCK API on http://127.0.0.1:8010 (dev only)'))
