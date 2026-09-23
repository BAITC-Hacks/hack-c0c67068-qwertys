# C5 — независимая строгая проверка модели

Проверено 23 сентября 2026, около 15:48 UTC+5. База аудита: `eace419`, неизменные результаты CPU V1/V2/V3. Проверка не запускала новое обучение, не использовала API, ключи, облако или дополнительные датасеты. Последующие GPU/V4-результаты требуют отдельной проверки.

## Вердикт

**Арифметика, сохранённые артефакты и временные разбиения проверенной версии воспроизводятся. Устойчивое преимущество DL и строгое соответствие исторической доступности погоды пока не доказаны.** Сохранять V1 основной до завершения заранее определённого приёмочного правила. Более сложная архитектура или GPU сами по себе не основание сменить модель.

| Гейт | Результат | Основание |
|---|---|---|
| Источник и целостность входов | PASS для локальных материалов | 440 погодных SHA; NPZ SHA; все признаки независимо собраны из соответствующих JSONL; все labels совпадают с полными часами C1 SCADA |
| Temporal split / preprocessing | PASS в изученном коде и артефактах | Нет общих target timestamps между train/validation и inner-fit/inner-stop; positive leads1–48; scaler и curve каждого checkpoint независимо пересчитаны исключительно по train |
| Сохранённая нейросеть соответствует отчёту | PASS | 24 SHA checkpoint; 24 реальных повторных inference из сохранённых весов, отклонение не более2e-7; 8 CSV совпадают с NPZ rows |
| Метрики | PASS | V1/V2 January RMSE, MAE, bias, horizons1–24/25–48 пересчитаны; V3 ensemble/curve RMSE и средние seeds совпадают до1e-12 |
| Устойчивое улучшение | NOT DEMONSTRATED | Descriptive3-day и5-day intervals включают0; повторно используемые December folds; часть срезов ухудшается |
| Историческая погода as-issued | UNCONFIRMED, блокирует безусловное заявление | `run+9h` — допущение, не исторический publication timestamp |
| Часовой пояс SCADA | UNCONFIRMED | UTC+6 — рабочая гипотеза, не подтверждение организатора |
| February accuracy | NOT EVALUABLE | Февральских фактических labels в выданных CSV нет; replay не является оценкой accuracy |
| Интеграция V3 в production | NOT CLAIMED | Веса outer-fold evaluation, отдельного production refit/adapter V3 нет; это честно описано C2 |

Это инженерная проверка, а не оценка жюри. Официальный DOCX разрешает участникам выбирать ML-модели и требует работающий почасовой прогноз24–48ч, архивы доступной тогда погоды, агентный пересчёт и февральский replay. Он не устанавливает обязательную глубину сети, GPU, nMAE8% или иной минимальный численный порог. Известной физической capacity для capacity-normalized ошибок нет.

## Независимо подтверждённые результаты

| Средний RMSE двух December folds, normalized_power | T1 | T2 |
|---|---:|---:|
| NWP curve V2 |0.26676639|0.26795361|
| CatBoost depth4 V2 |0.26294824|0.26626161|
| MLP, среднее трёх seeds |0.26131337|0.26445546|
| Feature Transformer |0.26430615|0.26461895|

MLP — лучший point estimate. Это компактная остаточная сеть, а attention-модель работает с семью признаками одного forecast hour, **не с временной последовательностью**. Называть её temporal Transformer нельзя.

Выборка содержит перекрывающиеся прогнозы: например T1 второго outer-fit имеет18454 issue/target pairs, но9263 уникальных target hours; validation766pairs/395hours. Тот же target при разных origins — допустимая единица прогнозирования с разным lead, но не независимое наблюдение. Дублированных одинаковых issue/target pairs не обнаружено. Группировка bootstrap по target-day сохраняет повторяющиеся origins одного target вместе, а3-day блоки частично учитывают временную зависимость. Текущие календарные дни в каждом fold непрерывны.

Bootstrap воспроизведён независимо. Для MLP минус curve3-day95% интервалы: T1[-0.023881,+0.014816], T2[-0.019906,+0.014950]. Проверка5-day также включает0. Циклическая граница блока искусственно соединяет конец/начало fold, блоки трёх/пяти дней не гарантируют захват всей погодной автокорреляции, зависимости между соседними folds не моделируются, семейства уже сравнивались. Поэтому это описательная чувствительность, **не доказательство значимости** и не prediction intervals.

January V1/V2 CSV воспроизводятся, но January уже открыт. Сравнение V2/V3/V4 не может вернуть ему статус нового независимого holdout. Evaluation fit cutoff Jan1 отличается от production refit cutoff Jan31; численные метрики не являются оценкой тех же самых production weights. Эта оговорка в отчётах C2 корректна.

## Найденные проблемы и действия

### P1 — историческая доступность не подтверждена

Evidence: поля weather `provenance_status=unconfirmed`, `availability_basis=inferred_run_plus_9h`; проверка лишь доказала выполнение заданного допущения. Impact: нельзя заявлять безусловное выполнение требования «доступно на момент выпуска». Fix: сохранить conditional статус в README/UI/экспорте; получить правило/разрешение организатора либо подтверждённый архив. Нельзя исправлять это увеличением сети или числом эпох. Аналогично не превращать UTC+6 в подтверждённый факт.

### P2 — неоднородная ошибка MLP и положительный high-wind bias

Evidence: на fold Dec15, forecast wind100>=8m/s, по171pairs на турбину, MLP RMSE T1 .323626 против curve .299819; T2 .313250 против .289228. Bias MLP +.140127/+.126314 против curve +.042958/+.044312. На первом fold high-wind MLP, наоборот, лучше. T2 lead25–48 первого fold также ухудшается .259086 против .256313. Impact: среднее улучшение маскирует ухудшение конкретных режимов; нельзя обещать надёжность на сильном ветре. Fix: заранее фиксированные срезы, калибровка остатка только внутри train, критерий отсутствия неприемлемой деградации. Источник срезов — `recomputed.json`; порог8m/s — диагностический wind slice, не норматив хакатона и не capacity.

### P2 — summarizer принимал неподтверждённый completed

Evidence: исходный `deep_report.summarize` считывал status/метрики из report.json, а CSV использовал для bootstrap без проверки SHA, seed completeness или соответствия метрик; две проверки были `assert` и исчезали при Python-O. Impact: изменённый CSV/checkpoint, неполный ensemble либо stale JSON могли получить убедительно выглядящую completed-сводку. Текущие опубликованные данные **не повреждены**, независимая проверка это подтвердила.

Fix в этой ветке: `verify_cell` проверяет SHA prediction/checkpoint, ровно три фиксированных seed, числовую конечность, уникальность issue/target, число rows, среднее seed-predictions и RMSE/MAE/bias; ошибки reference checks теперь ValueError. Два regressiontests воспроизводят повреждение CSV/checkpoint, missing seed и stale metric. Реальная сводка после исправления численно не изменилась. Это исправление QA, не новый модельный результат.

## Только два приоритетных направления улучшения

1. **Ограничить ненадёжную остаточную коррекцию MLP.** Один scalar alpha∈[0,1], без intercept: alpha=clip(sum(r*(y-base))/sum(r²),0,1), при нулевом знаменателе0. Рассчитать на inner-stop из модели, повторно обученной на inner-fit ровно selected_epochs; curve/scaler также inner-fit. Затем заморозить alpha для outer-refit. Не вычислять коэффициент на outer labels или последнем, а не выбранном epoch. Stoprule20мин на один заранее фиксированный эксперимент; качество оценить на одинаковых rows/срезах, без изменения Jan selection или подбора alpha по outer. Это гипотеза, не обещание улучшения.
2. **Проверить устойчивость к сезонному сдвигу и давности train.** Использовать уже разрешённую историю, фиксированные сезонные chronological folds и один recent91-day curve как drift-reference наряду с full curve. Сравнить одинаковые issue/target pairs, сохраняя inner boundaries и все seeds. Никакого нового большого grid search/чужого SCADA; stoprule20мин на один замороженный пакет. Недостаточный срез — insufficient evidence, не PASS. Все новые метрики остаются retrospective research.

Предложенный C2 V4 promotion gate 2% среднего выигрыша, не более5% ухудшения fold/достаточного slice и bias tolerance .01 допустим как **внутреннее заранее фиксированное инженерное правило**, но не норматив кейса и не доказанная бизнес-потребность. Нужно явно применять comparators к обеим curves и маркировать n<100 как недостаток доказательств. Успешный численный gate всё равно не заменяет целостность артефактов, inference/replay/API и provenance. При неуспехе не продлевать эксперимент автоматически и не менять пороги задним числом.

## Воспроизведение

Из корня worktree, с существующим optional PyTorch environment (без `.env`):

```powershell
<C2-python> docs/verification/model-quality/audit.py --c2-root <C2-worktree> --scada-dir <C1-hourly-directory> --output docs/verification/model-quality/recomputed.json
<C2-python> -m pytest tests/test_deep_compare.py tests/test_deep_report_integrity.py -q
<project-python> -m src.ml.deep_report --directory <C2-worktree>/artifacts/dl-v3/results --comparison coordination/research/C2/evaluation-v2-posttest.json --destination artifacts/c5-verified-summary.json
```

Observed: audit verified=true,440 hashes,24 restored weights; five selected tests PASS; verified summary completed with unchanged values. Артефакты аудитора содержат только агрегаты, SHA и методику; raw labels, weights, исходные CSV и секреты не коммитятся. Audit замечает CRLF рабочего checkout и сравнивает исходный training-file SHA с C2, дополнительно проверяя семантически тот же текст после нормализации переводов строк.

## Дополнение: локально выгруженный GPU V3

Отдельная проверка после CPU-аудита: ZIP2726367bytes, SHA256 `4f804e9d6f062f500e359a80c4d56c4a76ab565fda397474cebd8b447292a409`. Все35 выгруженных файлов побайтно соответствуют ZIP; 24 checkpoint и8 CSV проходят fail-closed SHA/seed/metric проверку. `report.json` указывает CUDA/TeslaT4, PyTorch2.14.0+cu126, LinuxAWS, runtime115.418s; CPU runtime614.75s. Dataset/codeSHA, config, seeds, fold boundaries/counts одинаковы. C5 не запрашивал облако повторно: hardware идентифицирован сохранённым training-report и runtime evidence C2.

| Mean fold RMSE | CPU T1 | GPU T1 | CPU T2 | GPU T2 |
|---|---:|---:|---:|---:|
| MLP |.26131337|.26097332|.26445546|.26505653|
| Feature Transformer |.26430615|.26179892|.26461895|.26336873|

Все GPU RMSE/MAE/bias и lead slices повторно рассчитаны из CSV; сводка и descriptive3-day intervals совпадают с экспортированными. **Все четыре интервала включают0**. GPU-факт подтверждает выполнение вычислений на заявленном устройстве в evidence C2, но не статистически надёжное улучшение; на T2 MLP GPU point estimate даже немного хуже CPU.

Все24 CUDA-trained checkpoints безопасно загружены `weights_only=True, map_location=cpu`, выполнен локальный inference. Максимальное расхождение с сохранёнными CUDA predictions: **3.4362077713e-5** (Transformer T2 Dec15 seed42); MLP максимум1.4156103e-7. Это НЕ cross-device exact PASS: исходный C2 tolerance2e-6 не выполнен для Transformer. Предел не увеличивался задним числом, проверка одинакового CUDA-device restore остаётся отдельной незавершённой задачей C2. Разные устройства допускают численные различия, но конкретная причина этим аудитом не установлена. Точные SHA/метрики подтверждены независимо от этого ограничения.

Воспроизведение без облака или нового обучения:

```powershell
<C2-python> docs/verification/model-quality/audit_gpu.py --c2-root <C2-worktree> --output docs/verification/model-quality/gpu-recomputed.json
```

Агрегаты: `gpu-recomputed.json`, `gpu-verified-summary.json`. Это дополнение относится только к замороженному V3; текущий V4 не принят автоматически.
