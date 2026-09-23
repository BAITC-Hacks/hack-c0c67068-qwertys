import type {
  ApiError,
  EventsResponse,
  Evaluation,
  ForecastResponse,
  Health,
  RunRequest,
  RunStatus,
} from './types'

export class HttpError extends Error {
  status: number
  api: ApiError | null
  constructor(status: number, api: ApiError | null, fallback: string) {
    super(api?.message ?? fallback)
    this.status = status
    this.api = api
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`/api${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    })
  } catch {
    throw new HttpError(0, { code: 'network', message: 'Backend недоступен (нет соединения с /api)', retryable: true }, 'network')
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
  createRun: (body: RunRequest) => request<RunStatus>('/runs', { method: 'POST', body: JSON.stringify(body) }),
  run: (id: string) => request<RunStatus>(`/runs/${encodeURIComponent(id)}`),
  forecast: (id: string) => request<ForecastResponse>(`/runs/${encodeURIComponent(id)}/forecast`),
  events: (id: string) => request<EventsResponse>(`/runs/${encodeURIComponent(id)}/events`),
  evaluation: () => request<Evaluation>('/evaluation'),
  exportUrl: (id: string) => `/api/runs/${encodeURIComponent(id)}/export.csv`,
}
