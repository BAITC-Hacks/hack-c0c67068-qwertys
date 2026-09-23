import { parseRows, validateResult } from './domain';
import type { AgentEvent, ForecastRequest, RunResult, RunStatus } from './types';

const base = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '');
export async function apiJson(path: string, signal: AbortSignal, init: RequestInit = {}): Promise<unknown> {
  const timeout = AbortSignal.timeout(20000);
  const response = await fetch(`${base}${path}`, { ...init, signal: AbortSignal.any([signal, timeout]), headers: { 'Content-Type': 'application/json', ...init.headers } });
  if (!response.ok) {
    // Do not reflect server traceback / credentials in the browser.
    throw new Error(response.status === 404 ? 'API расчёта пока недоступен (404). Проверьте запуск сервера.' : `Сервер не смог выполнить запрос (HTTP ${response.status}).`);
  }
  try { return await response.json(); } catch { throw new Error('Сервер вернул ответ не в формате JSON. Проверьте адрес API.'); }
}

function parseStatus(value: unknown): RunStatus {
  const status = value as RunStatus;
  if (!status || typeof status.run_id !== 'string' || typeof status.state !== 'string') throw new Error('Неверный формат статуса запуска.');
  return status;
}

function delay(ms: number, signal: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    if (signal.aborted) return reject(new DOMException('Aborted', 'AbortError'));
    const onAbort = () => { clearTimeout(timer); reject(new DOMException('Aborted', 'AbortError')); };
    const timer = setTimeout(() => { signal.removeEventListener('abort', onAbort); resolve(); }, ms);
    signal.addEventListener('abort', onAbort, { once: true });
  });
}

export async function runForecast(request: ForecastRequest, signal: AbortSignal, onStatus: (s: RunStatus) => void): Promise<RunResult> {
  let status = parseStatus(await apiJson('/runs', signal, { method: 'POST', body: JSON.stringify(request) }));
  const id = status.run_id;
  const end = Date.now() + 5 * 60000;
  const success = ['success', 'succeeded', 'completed', 'done'];
  while (!success.includes(status.state.toLowerCase())) {
    onStatus(status);
    if (['failed', 'error', 'cancelled', 'canceled', 'blocked'].includes(status.state.toLowerCase())) throw new Error(`Расчёт остановлен: ${status.state}. Проверьте журнал сервера.`);
    if (Date.now() > end) throw new Error(`Ожидание превысило 5 минут. Запуск ${id} может продолжаться на сервере.`);
    await delay(1500, signal);
    status = parseStatus(await apiJson(`/runs/${encodeURIComponent(id)}`, signal));
    if (status.run_id !== id) throw new Error('API вернул статус другого запуска.');
  }
  onStatus(status);
  const [forecast, eventsPayload] = await Promise.all([
    apiJson(`/runs/${encodeURIComponent(id)}/forecast`, signal),
    apiJson(`/runs/${encodeURIComponent(id)}/events`, signal),
  ]);
  const events = Array.isArray(eventsPayload) ? eventsPayload : (eventsPayload as { events?: unknown })?.events;
  if (!Array.isArray(events) || events.some(e => typeof e?.tool_name !== 'string' || typeof e?.state_transition !== 'string')) throw new Error('API вернул неверный журнал действий.');
  const result: RunResult = { status, request, rows: parseRows(forecast), events: events as AgentEvent[], mode: 'api', warnings: [] };
  result.warnings = validateResult(result);
  return result;
}
