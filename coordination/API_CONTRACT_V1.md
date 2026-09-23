# Минимальный контракт для C4 и Claude

Спецификация координации после запроса C4, не утверждение о работающем API. C4 реализует schemas/transport; C2 — numeric/agent; C1 — inputs; Claude — UI. Подтвердить ACK или конкретное несовместимое поле. Синтетический fixture разрешён только с явной меткой.

JSON snake_case. Timestamps RFC3339 с обязательным offset, ответы UTC Z. turbine_id: turbine_1/turbine_2. unit: normalized_power без неподтверждённого диапазона. Предлагаемые маршруты:

| Метод | Путь | Результат |
|---|---|---|
| GET | `/api/health` | status=ok, forecast_ready=true/false |
| POST | `/api/runs` | Вход issue_time, turbine_ids, horizon_hours24/48;202 с run_id,status=queued только после реального принятия;503 not_ready без ядра |
| GET | `/api/runs/{run_id}` | run_id,status,stage,mode,forecast_available,warnings,error |
| GET | `/api/runs/{run_id}/forecast` | run_id,unit,rows,metadata;409 not_ready до результата |
| GET | `/api/runs/{run_id}/events` | run_id,events; события seq,timestamp,tool,state,summary без секретов |
| GET | `/api/runs/{run_id}/export.csv` | UTF-8 CSV тех же rows;409 до результата |

status: queued/running/completed/failed. stage: weather/prepare/forecast/validate/export/null. mode: live/cached/deterministic, явно показан в UI. rows: turbine_id,issue_time,valid_time,lead_hours,y_pred. metadata: model_version,input_version,weather_provider,weather_model,weather_run_time,weather_available_at,availability_basis,scada_timezone,timezone_status,provenance_status. Неизвестное — null и предупреждение, не выдуманное значение.

Ошибки: `{ "error": { "code": "not_ready", "message": "Численная модель ещё не подключена", "retryable": false } }`. В RunStatus полеerror содержит внутренний объект либоnull. HTTP404 неизвестныйrun,422 неверныйвход,409 результатещёнеготов,503 отсутствуетядро/сервис. Уточнить конкретные ошибки в schemas, не возвращать фиктивные completed.

Обновление — новый POST/run_id, старый результат сохраняется. API не назначает произвольно origin: issue_time приходит явно; ежедневное расписание согласуется с C1/C2. Данные fixtures не выдаются за реальные forecasts. Исторические метрики до реализации отображаются как недоступные.

Локальные defaults: backend localhost:8000, UI localhost:5173, Vite proxy `/api`. Для активного запуска достаточно polling status/events с остановкой при completed/failed. Отдельный broker/WebSocket не обязателен. Это локальные параметры, не решение о публичном deployment.
