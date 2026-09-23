import type { ForecastRow, RunResult } from './types.ts';

export function timestamp(value: unknown): value is string {
  return typeof value === 'string' && /(?:Z|[+-]\d{2}:\d{2})$/.test(value) && Number.isFinite(Date.parse(value));
}

export function parseRows(payload: unknown): ForecastRow[] {
  const source = Array.isArray(payload) ? payload : (payload as { rows?: unknown })?.rows;
  if (!Array.isArray(source)) throw new Error('API вернул неверный формат прогноза: ожидается список rows.');
  const seen = new Set<string>();
  return source.map((raw: unknown) => {
    const row = raw as ForecastRow;
    if (!row || typeof row !== 'object' || typeof row.run_id !== 'string' || typeof row.turbine_id !== 'string'
      || !timestamp(row.issue_time) || !timestamp(row.valid_time)
      || !Number.isFinite(row.lead_hours) || row.lead_hours <= 0
      || Date.parse(row.valid_time) <= Date.parse(row.issue_time)
      || (row.y_pred !== null && (typeof row.y_pred !== 'number' || !Number.isFinite(row.y_pred) || row.y_pred < 0 || row.y_pred > 1))
      || typeof row.unit !== 'string') throw new Error('Некорректные значения, время или единицы в прогнозе API.');
    const actualLead = (Date.parse(row.valid_time) - Date.parse(row.issue_time)) / 3600000;
    if (Math.abs(actualLead - row.lead_hours) > 0.001) throw new Error('Горизонт строки не совпадает с её временными метками.');
    const key = `${row.turbine_id}|${Date.parse(row.issue_time)}|${Date.parse(row.valid_time)}`;
    if (seen.has(key)) throw new Error('API вернул повторяющиеся часы одного выпуска.');
    seen.add(key);
    return row;
  });
}

export function validateResult(result: RunResult): string[] {
  const { rows, request, status } = result;
  if (!rows.length) throw new Error('Расчёт завершён, но почасовой прогноз пуст.');
  if (rows.some(r => r.run_id !== status.run_id || Date.parse(r.issue_time) !== Date.parse(request.issue_time)
    || !request.turbine_ids.includes(r.turbine_id) || r.lead_hours > request.horizon_hours)) {
    throw new Error('Полученный прогноз не соответствует выбранному запуску.');
  }
  const warnings: string[] = [];
  for (const turbine of request.turbine_ids) {
    const count = rows.filter(r => r.turbine_id === turbine && r.y_pred !== null).length;
    if (count !== request.horizon_hours) warnings.push(`Турбина ${turbine}: доступно ${count} из ${request.horizon_hours} часов.`);
  }
  if (rows.some(r => r.fallback_status && !['none', 'false'].includes(r.fallback_status))) warnings.push('Часть прогноза рассчитана резервным методом. Подробности — в таблице.');
  if (status.weather?.available_at && Date.parse(status.weather.available_at) > Date.parse(request.issue_time)) {
    throw new Error('Погодный выпуск опубликован позже момента прогнозирования.');
  }
  if (!status.weather?.available_at) warnings.push('Время доступности погодного выпуска не передано сервером.');
  return warnings;
}

export function csvCell(value: unknown): string {
  let text = value == null ? '' : String(value);
  if (/^[=+@\-\t\r]/.test(text)) text = `'${text}`;
  return `"${text.replaceAll('"', '""')}"`;
}

export function makeCsv(result: RunResult): string {
  const keys: (keyof ForecastRow)[] = ['run_id', 'turbine_id', 'issue_time', 'valid_time', 'lead_hours', 'y_pred', 'unit', 'model_version', 'weather_reference', 'fallback_status'];
  return '\uFEFF' + [...['mode', ...keys].map(csvCell)].join(',') + '\r\n'
    + result.rows.map(row => [result.mode === 'example' ? 'SYNTHETIC_EXAMPLE' : (result.status.mode ?? 'api'), ...keys.map(k => row[k])].map(csvCell).join(',')).join('\r\n');
}

// Display a documented offset, never the browser's implicit timezone.
export function formatTime(value: string | undefined, offset = '+06:00', full = false): string {
  if (!value || !timestamp(value)) return 'Не указано';
  const sign = offset.startsWith('-') ? -1 : 1;
  const minutes = sign * (Number(offset.slice(1, 3)) * 60 + Number(offset.slice(4, 6)));
  return new Intl.DateTimeFormat('ru-RU', {
    timeZone: 'UTC', day: full ? '2-digit' : undefined, month: full ? '2-digit' : undefined,
    hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(new Date(Date.parse(value) + minutes * 60000));
}
