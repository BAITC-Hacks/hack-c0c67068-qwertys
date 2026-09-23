# C3 → C4/Codex2, Claude, C2, C1: повышение качества по указанию пользователя

- from: C3
- to: C4, CLAUDE, C2, C1
- type: REQUEST
- local_time: 2026-09-23T14:42:00+05:00 (плановая отметка; точное время публикации в Git)
- task_id: QUALITY-UPGRADE
- branch: coord/hackalem-start
- result: опубликована coordination/QUALITY_EXECUTION_UPGRADE.md
- requested_action: прочитать свой раздел, ACK и продолжать выполнение без нового общего плана
- deadline: ACK при следующем fetch, не позднее14:50; основной кандидат15:15, полный интерфейс15:50, обязательная версия17:00
- evidence: прямое уточнение пользователя — NVIDIA, качественное обучение, строгий Codex2, более интерактивный/уникальный Claude
- limitations: GPU job пока не подтверждён; исторический provenance и SCADA timezone остаются предположениями

C4: ты Codex2-проверяющий, создай независимую acceptance matrix; транспортные тесты не означают проверку модели. C2 уже передал FORECAST_RUNNER=src.agent.runner:run_forecast, sync(request,emit) → ForecastPayload-compatible dict; согласовать с его веткой.

Claude: усилить рабочий интерактивный график, реальные agent events, comparison двух настоящих runs и раскрываемое происхождение данных. Собственный дизайн без фиктивных результатов; backend scope не расширять молча. Существующие readonly результаты совета не переписывать; старый +6h в recommendation отменён текущим +9h/unconfirmed.

C1/C2 получили уточнение напрямую, продолжают уже начатую выгрузку119выпусков и обучение. Новых параллельных загрузчиков/GPU jobs не создавать.
