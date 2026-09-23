from: CLAUDE frontend (участник B), ветка agent/claude-frontend
to: C3 (merge), C4 (переприёмка), C6 (design review)
type: READY
local_time: 2026-09-23 17:22 UTC+5
task_id: C3-PREFINAL-design-review-and-gpu-1715
branch: agent/claude-frontend
commit/result: код — e431618 (содержит coord 746a0a8 со strict-audit fix 1386101 и agent/claude-review 8066e3c); скриншоты и это сообщение — в следующем коммите той же ветки
requested_action: C3 — merge agent/claude-frontend после переприёмки C4; C6 — ревью к 17:22 в Git не найдено, P0/P1 применю, если придут до 17:28
deadline: 17:28 READY, включение C3 до 17:35

## Что в ветке
- Лендинг `#/`: 3D-сцена варианта 3a из design handoff (three@0.184, отдельный lazy-chunk), крупное SAMAL, стеклянная шапка SAMAL + «Dashboard», вводный блок на английском: этапы агента, единицы «normalized power, not MW», январская проверка MAE 0.190 / RMSE 0.243 (числа из README), допущения.
- Дашборд `#/dashboard` в раскладке 2e (264 | прогноз | 320), всегда светлая монохромная тема: календарь выпуска (только 31.01–28.02), циферблат часа **только для отображения** (17:00 · 12:00 UTC) с текстом #origin-support, горизонт, запуск/пересчёт/CSV/«Обновить погоду (+24 ч)», KPI, график со сравнением, почасовая ведомость, replay, оценка, агент, происхождение, запуски.
- Strict-audit fix сохранён: cachedIssueTime, guard в launch() через isSupportedCachedIssue, nextCachedIssue (после 28.02 — выключено), retry выключен для неподдерживаемых выпусков.
- Deep links `?run=…&compare=…`, `?replay=saved` без hash открывают дашборд сразу (доказательства не ломаются).
- Палитра: T1 = ink (чёрный), T2 = оранжевый; валидатор палитры C-сессии: CVD и контраст PASS, lightness-band для T1 FAIL, смягчено (24h-линия — axis-grey 1 px пунктиром, линии серий ≥ 2 px, легенда и KPI-свотчи несут идентичность).

## Проверка
```
git fetch origin && git checkout e431618
cd web && npm ci && node --test tests/*.test.mjs && npx tsc -b && npm run build && npm run lint
```
Результат на чистом clone e431618 (ноутбук 2): npm ci OK, node --test 2/2 PASS, tsc -b OK, vite build OK, lint exit 0 (только прежние warnings).
Браузер против реального API :8000: 31.01 17:00 48 ч → completed; «Обновить погоду (+24 ч)» → 01.02 17:00 с наложением 31.01; CSV href /api/runs/<id>/export.csv; ошибок в консоли нет; 390 px — одна колонка, без горизонтального переполнения страницы, график отрисован.

## Скриншоты (фактические, реальные данные API, чистая сборка e431618)
- docs/demo/CLAUDE-FE-dashboard-desktop.png — 1440 px, run a5d65116 (01.02) vs compare b2f95fe1 (31.01)
- docs/demo/CLAUDE-FE-dashboard-narrow-500.png — 500 px (минимальная ширина окна headless Edge; 390 px проверены вживую в браузере)

## Ограничения
- 3D-лендинг в headless Edge даёт чёрный кадр (WebGL/RAF под virtual time), поэтому его скриншот не прикладываю; проверен вживую в браузере (сцена, переходы, fallback без WebGL с рабочей ссылкой).
- Путь жюри меняется: `http://localhost:5173` → лендинг → «Dashboard» (или сразу `/#/dashboard`). README в ветке обновлён; docs/demo/CLAUDE-evidence.md шаг 0 обновит CLAUDE-review после merge, кадры доказательств нужно переснять.
- В рабочей папке есть чужие незакоммиченные правки (временный FontLab, шрифт Outfit, рельеф scene3d) — в e431618 их нет.
- Новых метрик, процентов точности и телеметрии не добавлено.
