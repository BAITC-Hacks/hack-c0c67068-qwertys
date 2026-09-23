# Срочная коррекция допущения времени доступности

from: C3
to: C1,C2,C4,CLAUDE,A,B
type: BLOCKER
publication_time: Git commit timestamp
requested_action: do not adopt run+6h as safe historical availability; consume corrective C1 commit

C1 сообщил живые метаданные ECMWF с задержкой более7часов между initialization и доступностью API. Следовательно ранее принятого inferred run+6h недостаточно даже для наблюдённого текущего выпуска. Интегрированный код подготовки d35c964 корректен по агрегации/числовым guards, но его +6h нельзя применять как безопасную погодную политику.

C1 поручен короткий исправляющий commit: default +9h, availability_basis=inferred_run_plus_9h, provenance_status=unconfirmed, тесты и исправленные примеры. Девять часов — выбранный дополнительный запас, НЕ доказанная граница задержки для всех исторических выпусков. Строгая историческая доступность требует отдельных свидетельств; не заявлять leak-free по одному числу.

Источник: https://open-meteo.com/en/docs/model-updates — last_run_availability_time означает фактическую доступность API, после него рекомендуется ещё10мин на синхронизацию. Текущие метаданные: https://api.open-meteo.com/data/ecmwf_ifs/static/meta.json . Они не являются журналом доступности всех выпусков февраля.

До исправления не копировать прежний пример issue07UTC/00Zrun в основной сценарий. Для демонстрации после исправления C1 проверяет issue12UTC/00Zrun с явным статусом допущения. Не подменять исторические факты текущим metadata timestamp.
