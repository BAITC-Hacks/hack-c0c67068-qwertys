# Воспроизводимость SAMAL

Команды выполняются из корня репозитория после установки по [README](../README.md). Данные, кэши и исследовательские веса хранятся локально.

## Данные и настройки

Получите два исходных CSV из официальной выдачи организаторов. Не загружайте их в Git. Файлы содержат 142 360 и 149 499 строк с шагом около 10 минут за 11.03.2023–31.01.2026. Факта за февраль 2026 нет, хотя февраль указан в названиях файлов.

```powershell
.venv/Scripts/python.exe scripts/verify_data.py "PATH_TO_OFFICIAL_CSV_DIRECTORY"
```

Команда сверяет размер и SHA-256 с [манифестом](../coordination/DATA_MANIFEST.json), не изменяя CSV. Обе контрольные суммы проверены на ноутбуке 2.

Скопируйте `.env.example` в `.env`, задайте необходимые локальные параметры:

| Переменная | Назначение |
|---|---|
| `MODEL_DIR` | Каталог с manifest.json; по умолчанию models/production |
| `WEATHER_RUNS_DIR` | Для приведённых команд C1: artifacts/c1/weather_runs |
| `AGENT_MODE` | deterministic для проверенного сценария; live/auto требуют согласованного доступа и расходов |
| `RUN_STORE_PATH` | SQLite-журнал; по умолчанию `.local/runs.sqlite3` |
| `FORECAST_RUNNER` | `src.agent.runner:run_forecast`; пусто — честный `not_ready` |
| `OPENAI_API_KEY`, `OPENAI_MODEL` | Только для реализованного LLM-режима ядра; не требуются для запуска HTTP API |
| `WEATHER_FETCH_POLICY` | never — проверенный локальный кэш; missing/refresh — явное обращение к погодному источнику |
| `OPENAI_SESSION_BUDGET_USD` | Локальный лимит агента; по умолчанию1USD, в пределах согласованного общего бюджета |
| `EVALUATION_PATH` | JSON исторических метрик; по умолчанию coordination/research/C2/evaluation-v1.json |

Ключи не передаются в браузер и не коммитятся. Детерминированному режиму API-ключ не нужен. Health проверяет наличие модели/погодного кэша; покрытие конкретной даты проверяется в расчёте.

## Обучение, метрики и февральский replay

```powershell
.venv/Scripts/python.exe -m src.data.scada --input "PATH_TO_TURBINE_1.csv" --turbine-id turbine_1 --output artifacts/c1/scada-t1-hourly.jsonl --report artifacts/c1/scada-t1-report.json
.venv/Scripts/python.exe -m src.data.scada --input "PATH_TO_TURBINE_2.csv" --turbine-id turbine_2 --output artifacts/c1/scada-t2-hourly.jsonl --report artifacts/c1/scada-t2-report.json
.venv/Scripts/python.exe -m src.weather.batch_archive --start-date 2025-11-01 --end-date 2026-02-28 --sleep-seconds 1
.venv/Scripts/python.exe -m src.weather.verify_archive --start-date 2025-11-01 --end-date 2026-02-28
.venv/Scripts/python.exe -m src.ml.train --scada-dir artifacts/c1 --weather-dir artifacts/c1/weather_runs --output-dir models/production --report artifacts/evaluation.json
.venv/Scripts/python.exe scripts/verify_evaluation.py --report artifacts/evaluation.json --scada-dir artifacts/c1 --weather-dir artifacts/c1/weather_runs --output artifacts/independent-metrics.json
.venv/Scripts/python.exe -m src.cli.replay --model-dir models/production --weather-dir artifacts/c1/weather_runs --output-dir artifacts/replay
```

Два расширяющихся временных validation-fold до января сравнивают baseline NWP→power с тремя фиксированными вариантами CatBoost. В обоих случаях выбран baseline. Январские метрики ниже относятся к моделям, обученным только на targets до `2026-01-01T00:00:00Z`. После оценки production V1 отдельно переобучена на пригодных targets строго до `2026-01-31T00:00:00Z`: это та же выбранная модельная схема, но другие обученные параметры. Показанные метрики не являются измерением этих production-весов. Признаки не используют будущую SCADA. Единица метрик — пара (issue_time, target_hour), вес каждой пары 1; перекрывающиеся выпуски сохранены.

Независимо воспроизведено: обучение 15,328с; 1390 январских пар на турбину, 707 уникальных целевых часов. Метрики в исходных нормализованных единицах:

| Турбина | Baseline MAE | Baseline RMSE | CatBoost RMSE | Bias baseline (прогноз−факт) |
|---|---:|---:|---:|---:|
| Т1 | 0,190351 | 0,243279 | 0,253398 | +0,074741 |
| Т2 | 0,190407 | 0,243430 | 0,254650 | +0,073179 |

[Независимые метрики](../docs/verification/independent-metrics.json) включают lead 1–24/25–48 и SHA. Проверяющий скрипт не импортирует модель: сам пересчитывает метрики из CSV, сверяет labels с SCADA, покрытие и времена. [Отчёт C2](../coordination/research/C2/evaluation-v1.json) содержит validation/trials. Численные метрики совпали в пределах 1e-12; SHA повторно загруженных HTTP-ответов и model_version могут отличаться из-за служебных полей, что не доказывает различие численных данных.

Актуальный replay C2 включает 29 ежедневных выпусков 31.01–28.02. Независимо воспроизведены 2784 строки полного журнала и 1344 уникальных прогноза (672 часа × 2 турбины). В новом UUID-каталоге — manifest.json, all-issues.csv, february.csv и отдельные запуски. Календарь февраля использует гипотезу UTC+6; для каждого часа выбран самый новый сохранённый выпуск с lead≥1. Правило предложено командой, не подтверждено организатором. Это прогноз/replay, **не измеренная точность февраля**.

Отдельная v2 использует 440 погодных выпусков за 2024-11-12–2026-01-30 и один зафиксированный вариант CatBoost depth4/full. Она выполнена после просмотра января, поэтому её январские числа — **post-test диагностика**, не новая независимая оценка. C4 воспроизвёл обучение за61,656с и независимо сверил все метрики/выбор с отчётом C2. Преимущество на всех проверках не показано; принятая v1 остаётся по умолчанию. [Точные команды и результаты v2](../docs/verification/v2-reproduction.md). Для исполнения v2 нужны обученные `.cbm`, одного model-manifest-v2.json недостаточно.

В интерфейсе отчёты разделены на «v1 · независимая оценка» и «v2 · post-test эксперимент»; переключение вкладки не меняет рабочую модель. Независимость здесь означает отдельный пересчёт проверяющим: это первоначальная январская временная проверка при неподтверждённой исторической доступности погоды, не внешний независимый benchmark. `GET /api/evaluation?variant=v2` читает `EVALUATION_V2_PATH`, по умолчанию `coordination/research/C2/evaluation-v2-posttest.json`.

