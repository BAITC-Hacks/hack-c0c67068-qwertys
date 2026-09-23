# README skeleton (CLAUDE, DOC-01) — to be filled ONLY with verified facts

Required by rules §5.4.15 / §5.6.4; every section below must exist in the final README. `TBD` = not yet implemented/verified — never replace with a plan.

1. **Что это и для кого** — диспетчер/планировщик ВЭС: почасовой прогноз нормализованной мощности 2 турбин на 24–48 ч. (1 абзац)
2. **Быстрый старт (≤5 команд)** — Windows/Linux, Python 3.12: clone → venv → `pip install -r requirements.txt` → положить CSV в `data/raw/` (имена и SHA-256 из `coordination/DATA_MANIFEST.json`) → одна команда replay → где смотреть результат. TBD
3. **Основной сценарий проверки** — что эксперт запускает и что именно должен увидеть (число строк, файлы, журнал агента, пересчёт). TBD
4. **Архитектура** — диаграмма: Weather tool (Open-Meteo Single Runs, ECMWF IFS) → Data tool (SCADA hourly) → Model tool → Analyze/Validate → Recompute on update → Export/UI; где LLM, где детерминированный код. TBD
5. **Агентный цикл** — список инструментов, состояния, правила решения, повторы, журнал (пример реального фрагмента). TBD
6. **Защита от утечки** — issue_time, правило available_at (init + latency), отсутствие февральских лагов, timezone SCADA (гипотеза UTC+6 + проверка). TBD
7. **Модель и качество** — baseline(ы), модель, протокол rolling-origin на истории до февраля, таблица MAE/RMSE по турбинам и горизонтам 1–24/25–48 ч. Метрик за февраль нет (факта нет). TBD
8. **Результат** — `outputs/…csv`, схема колонок, правило перекрытия 48-ч горизонтов. TBD
9. **Технологии и зависимости** — версии из requirements. TBD
10. **Переменные окружения** — `.env.example`; LLM-ключ опционален, без него детерминированный режим (помечен). TBD
11. **Офлайн-режим** — кэш архивных прогнозов погоды в репозитории. TBD
12. **Ограничения** — неизвестная нормализация (не МВт), timezone inferred, архив ECMWF provenance, одна сеточная точка на обе турбины. TBD
13. **Развитие** — roadmap из совета. TBD
14. **Команда и роли** — кто что делал (коммиты).
