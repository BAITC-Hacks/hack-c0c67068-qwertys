# C4 independent V2 reproduction

2026-09-23 ~15:26 UTC+5, laptop2, Python3.12.10 and shared pinned environment. V1 production was not changed. V2 is explicitly post-test: January had already been seen before the extended-history experiment.

Reproduced the exact **date set** of C2 snapshot `37f6e9e1b362d8530b76f37675aea415291fa508e57b6487ce786f95773af43a`:440daily cycles,2024-11-12..2026-01-30. Reused91 already verified local cycles, independently fetched349 with C1 bounded/resumable loader and1s spacing. Excluded the same11early hindcast dates and5missing dates2025-08-05..09. No unexpected dates. C1 verifier passed all349new raw SHA/finite/coverage checks. Re-fetching source responses changes response metadata/hash: this is not a claim of byte-identical C2 archive or identical model artifact SHA.

Local directories (ignored): `artifacts/c4/v2-weather`, `artifacts/c4/v2-raw`, `artifacts/c4/v2-weather-manifest.json`. Each downloader invocation must cover at most125dates. Reproduction chunks:

- 2024-11-12..2025-03-16;
- 2025-03-17..2025-07-19;
- 2025-07-20..2025-08-04;
- 2025-08-10..2025-10-31;
- copy verified daily JSONL2025-11-01..2026-01-30 from the existing C1 cache.

Use `python -m src.weather.batch_archive --start-date START --end-date END --output-dir artifacts/c4/v2-weather --cache-dir artifacts/c4/v2-raw --manifest artifacts/c4/v2-weather-manifest.json --sleep-seconds 1` for each range. No dates were added to improve the result.

```powershell
.venv/Scripts/python.exe -m src.ml.train --scada-dir artifacts/c1 --weather-dir artifacts/c4/v2-weather --output-dir models/extended-v2 --report artifacts/evaluation-v2/evaluation.json --fixed-candidate depth4_full --experiment-label post-test-extended-history
.venv/Scripts/python.exe scripts/verify_evaluation.py --report artifacts/evaluation-v2/evaluation.json --scada-dir artifacts/c1 --weather-dir artifacts/c4/v2-weather --reference-report coordination/research/C2/evaluation-v2-posttest.json --output artifacts/independent-v2-metrics.json
.venv/Scripts/python.exe -m src.cli.replay --model-dir models/extended-v2 --weather-dir artifacts/c1/weather_runs --output-dir artifacts/replay-v2
```

Observed training61.656s, local model `nwp-tabular-0a51dc19195e`, two real CatBoost artifacts. All pretest-fold/trial scores, selection and sample counts match C2 within1e-10. Independent stdlib recomputation matches every reported January MAE/RMSE/bias/n for curve, CatBoost and persistence, including lead1–24/25–48. Persistence independently checked against the last complete observed hour available at each issue. Actual labels independently joined from verified local SCADA.1390pairs/707unique target hours per turbine, no silent omission; overlapping origins retained.

| Turbine | V2 curve January RMSE | V2 selected CatBoost January RMSE | V1 selected curve January RMSE |
|---|---:|---:|---:|
|T1|0.2327964013|0.2436901401|0.2432793678|
|T2|0.2341826149|0.2460638455|0.2434300073|

These V2 January values are diagnostics after prior test access. Do not select the January-winning V2 curve post hoc or claim an untouched second test. The frozen V2 fold rule selected depth4/full CatBoost; there is no demonstrated universal accuracy improvement over V1. C4 recommendation: retain the accepted V1 default, expose V2 as a reproducible separate experiment.

Actual V2 forecast96rows PASS; replay29issues/2784journal rows/1344final rows PASS, local output `artifacts/replay-v2/387a722cfbb2407d9ab0953cfd1f1408`. This does not provide February accuracy: labels are absent. Weather publication/timezone remain inferred.

Machine-readable independent result: [independent-v2-metrics.json](independent-v2-metrics.json). The verifier imports no C2 metric/model functions. No raw labels, model binaries or weather cache are committed.
