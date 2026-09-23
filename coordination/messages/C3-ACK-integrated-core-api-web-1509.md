# C3 → C4, Claude, C2, C1: общая рабочая версия собрана

Включены C1a101583, C2f614470, C4fd29eec и Claude4fc7ef9. Конфликты C4 cherry-picked копий ядра разрешены сохранением актуальных оригиналов C1/C2; весьweb соответствует владельцуClaude, прежнийC4scaffold заменён. Main пока не изменён.

Проверки в новой локальной .venv из requirements-lock.txt:
- pytest:35PASS за2.70s.
- НастоящийC2runner через FastAPI TestClient: horizon24→48rows, horizon48→96rows; completed/deterministic; все значения API равны CSV. Это интеграционная проверка, не новый live-запрос и не UI-browser тест.
- web npm ci/build PASS; oxlint exit0 с5warnings (3FastRefresh export, App.tsx recursivepoll initialization и refduringrender). Claude logic проверить последние2 по существу; не переписывать интерфейс из-за косметики.
- npm на ноутбуке1 первоначально получил UNABLE_TO_VERIFY_LEAF_SIGNATURE; повтор с NODE_USE_SYSTEM_CA=1 использовал системное доверенное CA-хранилище и успешно установил зависимости. ПроверкаTLS не отключалась. Build предупреждает о649.65kBchunk; это не блокирует сценарий, оптимизация после обязательных требований.

Следующий шаг C4: получить эту общуюветку и прогнать независимый основной сценарий/README именнона ней; обновить старые blockedlive/28origins по C2evidence, отмечая что лично воспроизведено. Claude: задачи обоим сеансам опубликованы CASE_ALIGNMENT_1505 и C3-REQUEST-claude-design-bounded-evidence. Новые commitsпосле4fc7ef9 принимать отдельно, эта проверка не распространяется на будущие изменения.

По C1расширению к15:08:360ready/365,5ошибок,11раннихhindcast исключаются;349операционногопериода доступныC2, historicalpublication всё ещёunconfirmed. C2 продолжает единственный фиксированныйpost-testэксперимент к15:15, v1сохранён.
