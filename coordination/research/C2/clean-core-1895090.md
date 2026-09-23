# Чистый запуск основной модели — PASS

C2, 23.09.2026, 16:20 UTC+5. Проверен **Git 1895090** через `git archive`, без `.git`, `.env`, исходных SCADA, прежних моделей или погодного кэша. Все274 экспортированных файла после проверки побайтно совпали с ZIP. Отличия от интеграционных9265489/b157f4d — только документация; `src`, `scripts` и lock не изменены.

Новый каталог: `D:\HACKALEM\verification\c2-clean-1895090-20260923`, за пределами всех worktree. В нём создана новая venv Python3.12.14 без system-site-packages. Установлены и сверены все46 версий requirements-lock.txt; `pip check` PASS. Pip использовал ранее загруженные wheel-файлы своего кэша, но пакеты из другой venv не копировались. PyTorch отсутствует и для V1 не нужен.

Из tracked `coordination/research/C2/model-manifest-v1.json` скопирован самодостаточный manifest: `nwp-tabular-7f1b4f31e9bb`, SHA256 `a4159d859b3dcc743ca230ca7f5fb8412752f7e1abb31718d6b5f0c3833dbd1e`. Ни обучения, ни обращения к прежним worktree во время исполнения не было. Штатная команда заново скачала один выпуск Open-Meteo2026-01-31;48часов покрыты, ответ2639bytes/SHA `3c0a5be5fa0d4c04e98d7d095efc51601593698e2d5bea2d1819b834c67b6a9e`.

**Результаты:** CLI48ч/24ч →96/48строк, точное равенство CSV/JSON и совпадение общего горизонта; readiness PASS. Затем штатные `run_local.py` и `smoke_api.py` → три настоящих deterministic-запуска96/48/96строк, CSV/API равны, все5инструментов выполнены, старый результат сохранён. Время API0.2593/0.2358/0.1979с на этой машине. Во всех пяти запусках0LLM-запросов/0токенов/0USD. Временный сервер8011 после проверки остановлен; основное демо8010 не затрагивалось.

## Команды для README

Из каталога репозитория экспортировать в новый пустой каталог (имя уникально, ничего не удаляется):

```powershell
$cleanRoot = Join-Path $env:TEMP ('hackalem-clean-' + [guid]::NewGuid().ToString('N'))
$cleanZip = $cleanRoot + '.zip'
git archive --format=zip -o $cleanZip 1895090
Expand-Archive -LiteralPath $cleanZip -DestinationPath $cleanRoot
Set-Location $cleanRoot
```

В чистом каталоге, используя установленный Python3.12:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-lock.txt
.venv/Scripts/python.exe -m pip check
$env:PYTHONPATH=''
$env:PYTHONNOUSERSITE='1'
$env:PYTHON_DOTENV_DISABLED='1'
$env:OPENAI_API_KEY=''
$env:AGENT_MODE='deterministic'
$env:MODEL_DIR='models/production'
$env:WEATHER_RUNS_DIR='artifacts/c1/weather_runs'
$env:WEATHER_FETCH_POLICY='never'
New-Item -ItemType Directory models/production
Copy-Item coordination/research/C2/model-manifest-v1.json models/production/manifest.json
.venv/Scripts/python.exe -m src.weather.batch_archive --start-date 2026-01-31 --end-date 2026-01-31 --sleep-seconds 1
.venv/Scripts/python.exe scripts/run_local.py --check
.venv/Scripts/python.exe -m src.cli --issue-time 2026-01-31T12:00:00Z --horizon-hours 48 --model-dir models/production --weather-dir artifacts/c1/weather_runs --output-dir artifacts/clean-runs --agent-mode deterministic
.venv/Scripts/python.exe -m src.cli --issue-time 2026-01-31T12:00:00Z --horizon-hours 24 --model-dir models/production --weather-dir artifacts/c1/weather_runs --output-dir artifacts/clean-runs --agent-mode deterministic
.venv/Scripts/python.exe scripts/run_local.py --port 8011 --agent-mode deterministic
```

В другом терминале из того же чистого каталога:

```powershell
.venv/Scripts/python.exe scripts/smoke_api.py --base-url http://127.0.0.1:8011 --issue-time 2026-01-31T12:00:00Z
```

В проведённом эксперименте для создания venv использован установленный Python `C:\Users\Шахназар\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`; это базовый интерпретатор, не Python другой рабочей копии. Все последующие команды использовали новую `.venv/Scripts/python.exe`. При фактической проверке HTTP отдельно заданы локальные FORECAST_OUTPUT_DIR=artifacts/api-runs и RUN_STORE_PATH=.local/clean-runs.sqlite3 для разделения доказательств CLI/API; это необязательно для обычного запуска.

## Граница результата

Core-blockers не найдены. Эта проверка касается чистой установки ядра, реальной сетевой загрузки погоды, CLI и HTTP. Frontend в этом каталоге не собирался; новые тесты обучения не запускались, качество модели не переоценивалось. Историческая доступность погоды+9ч и SCADA UTC+6 остаются предположениями; февральских наблюдений нет. Ответ поставщика при повторном запросе может отличаться служебными полями и SHA, поэтому численный результат следует сравнивать отдельно.

Машинное доказательство: `clean-core-1895090.json`. Проверяющий скрипт `verify_clean_core.py` — копия реально исполненного файла; для повторной проверки скопировать его в корень чистого экспорта после выполнения команд, передать путь к исходному Git ZIP и сохранить api-smoke.json. Скрипт не обучает модели и не вызывает API; он сверяет архив, зависимости, происхождение модулей, модель, сохранённую погоду, прогнозы и usage. Автоматического заявления о повторном скачивании или чистоте каталога без описанной процедуры сам по себе он не доказывает.
