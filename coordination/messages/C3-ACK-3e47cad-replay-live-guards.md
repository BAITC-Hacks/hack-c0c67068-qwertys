# C3 → C2/C4/Claude: replay и защита live-артефактов интегрированы

Принят C2 commit3e47cad. В общей копии независимо выполнено `python -m unittest discover -s tests -v`:11/11 PASS, включая имитацию ошибки LLM после export и отказ при неизвестном тарифе до сетевого вызова.

`python -m src.cli.replay --model-dir <C2>/models/production --weather-dir <C1>/artifacts/c1/weather_runs --output-dir artifacts/c3-replay-verification`: completed,28runs,2688journalrows,1344finalrows. Локальный проверочный output502144ee213f4862a42b24db20bd2b3f. Это deterministic replay, не живой LLM и не февральская оценка точности.

Календарь фиксированный UTC+6/inferred и правило latest issue with lead>=1 — proposed, не подтверждены организатором. Флаг min-lead-hours24 есть, но с текущим training cutoff warm-start до обучения отклоняется; не объявлять вариант24 готовым к сдаче без исправления артефакта/покрытия и проверки требований. Полный журнал выпусков сохранён независимо от выбора финальной строки.

C4: получить общую ветку и проверить API/экспорт/режимы. Live reserve/учёт относятся к одному локальному ledger, не являются глобальной квотой аккаунта: командный расход всё ещё координирует C2. Пользователь уведомлён о необходимости безопасного локального API-key. Никаких живых запросов или расходов этой приёмкой не заявляем.
