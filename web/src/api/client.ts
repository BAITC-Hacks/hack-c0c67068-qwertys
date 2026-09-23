import type {
  ApiError,
  EventsResponse,
  ForecastResponse,
  Health,
  RunRequest,
  RunStatus,
} from './types'
import type { EvaluationV1 } from '../components/EvaluationPanel'

export class HttpError extends Error {
  status: number
  api: ApiError | null
  constructor(status: number, api: ApiError | null, fallback: string) {
    super(api?.message ?? fallback)
    this.status = status
    this.api = api
  }
}

const TIMEOUT_MS = 20_000

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  const ctrl = new AbortController()
  const timer = window.setTimeout(() => ctrl.abort(), TIMEOUT_MS)
  try {
    res = await fetch(`/api${path}`, {
      ...init,
      signal: ctrl.signal,
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    })
  } catch {
    const timedOut = ctrl.signal.aborted
    throw new HttpError(
      0,
      timedOut
        ? { code: 'timeout', message: `Нет ответа от /api за ${TIMEOUT_MS / 1000} с`, retryable: true }
        : { code: 'network', message: 'Backend недоступен (нет соединения с /api)', retryable: true },
      'network',
    )
  } finally {
    window.clearTimeout(timer)
  }
  if (!res.ok) {
    if ([502, 504].includes(res.status) && !res.headers.get('content-type')?.includes('json')) {
      throw new HttpError(res.status, { code: 'backend_down', message: 'Backend недоступен (прокси /api не получил ответа)', retryable: true }, 'down')
    }
    let api: ApiError | null = null
    try {
      const body = await res.json()
      api = body?.error ?? (body?.detail ? { code: String(res.status), message: String(body.detail), retryable: false } : null)
    } catch {
      /* non-JSON error body */
    }
    throw new HttpError(res.status, api, `HTTP ${res.status}`)
  }
  return (await res.json()) as T
}

export const api = {
  health: () => request<Health>('/health'),
  runs: () => request<RunStatus[]>('/runs'),
  createRun: (body: RunRequest) => request<RunStatus>('/runs', { method: 'POST', body: JSON.stringify(body) }),
  run: (id: string) => request<RunStatus>(`/runs/${encodeURIComponent(id)}`),
  forecast: (id: string) => request<ForecastResponse>(`/runs/${encodeURIComponent(id)}/forecast`),
  events: (id: string) => request<EventsResponse>(`/runs/${encodeURIComponent(id)}/events`),
  evaluation: () => request<EvaluationV1>('/evaluation'),
  exportUrl: (id: string) => `/api/runs/${encodeURIComponent(id)}/export.csv`,
}
