# Frozen extended-history experiment, completed15:10 UTC+5

V1 remains unchanged and accepted by C4. V2 is a separate trained candidate, **post-test** because January was already opened. No new configuration search: fixed CatBoostdepth4/full,400iterations,lr0.04,seed42,4CPUthreads versus the same1m/s learned NWP curve; same2Decemberfolds. NoGPU used for these results.

Snapshot:440daily00Z weather runs,2024-11-12..2026-01-30, SHA37f6e9e1b362d8530b76f37675aea415291fa508e57b6487ce786f95773af43a. This combines349extended+91original runs. Excluded11early49r1hindcastdatesNov1–11,2024. Five faileddatesAug5–9,2025 are absent, never interpolated. All remaining weather availability is still unconfirmed, +9h inferred. Full date/SHA index in v2-snapshot.json.

| Turbine | Training pairs / unique target hours (beforeDec15) | V1 curve mean foldRMSE | V2 curve mean foldRMSE | V2 CatBoost mean foldRMSE | Selected by frozen fold rule |
|---|---:|---:|---:|---:|---|
| turbine_1 |18454 /9263|0.269409|0.266766|0.262948|depth4_full|
| turbine_2 |18406 /9239|0.272658|0.267954|0.266262|depth4_full|

Candidate wins both T1folds but only second T2fold; T2firstfold0.254654 versuscurve0.253799. Candidate trainRMSE≈0.229–0.231, validation≈0.246–0.280; do not claim confidence intervals or dramatic gain. Final choice in V2artifact follows the frozen mean-fold criterion even though Januarydiagnostics below are less favorable.

| Turbine | V1 chosen curve JanuaryRMSE | V2 curve JanuaryRMSE | V2 CatBoost JanuaryRMSE | V2 CatBoost MAE / bias |
|---|---:|---:|---:|---:|
| turbine_1 |0.243279|0.232796|0.243690|0.188855 /+0.087160|
| turbine_2 |0.243430|0.234183|0.246064|0.190427 /+0.087220|

Januaryvalues are **post-test diagnostics**, not a new untouched test or basis to replace the frozen selection with the Januarywinner.1390pairs/707unique targethours/turbine,100%ofeligiblepairs. Perlead1–24/25–48 MAE/RMSE/bias,fold details,counts,versions,SHA and estimatorcutoffs in evaluation-v2-posttest.json. Normalizedpowerunits, bias=prediction-actual; no MW/capacitynormalization.

Training41.0s. Model nwp-tabular-0079962f502f. Local `models/extended-v2/manifest.json` plus turbine_1.cbm138712bytes and turbine_2.cbm138680bytes (hashes in model-manifest-v2.json). Manifest alone is NOT a runnable model. No raw labels or binarymodels added toGit. Originalv1models/production unchanged.

```
python -m src.ml.train --scada-dir <C1_hourly> --weather-dir <440run_snapshot> --output-dir models/extended-v2 --report artifacts/evaluation-v2-posttest/evaluation.json --fixed-candidate depth4_full --experiment-label post-test-extended-history
python -m src.cli --issue-time 2026-01-31T12:00Z --model-dir models/extended-v2 --weather-dir <replay_weather_runs> --agent-mode deterministic
python -m src.cli.replay --model-dir models/extended-v2 --weather-dir <replay_weather_runs> --output-dir artifacts/replay-v2
```

Real forecast96rows and replay29issues/2784journal/1344selected rows PASS. Private metricCSV in artifacts/evaluation-v2-posttest/ supports independent C4 recomputation. Frozen release v1 remains the default while C3/C4 assess this separate candidate; do not silently label its productionweights as the estimator evaluated on January. No Februarylabels/metrics. PendingAWSconsent is separate and did not block this completed CPUexperiment.
