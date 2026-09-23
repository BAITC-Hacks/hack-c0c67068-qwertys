# V4 bounded quality cycle — frozen before results

23 September 2026, 15:47 UTC+5. User requested a further 2.5-hour quality effort; C3 confirmed results by16:30, one existingT4 stop≤16:40, integration17:00. This is retrospective post-test research. January was already viewed in V1/V2; it is excluded from this experiment. Earlier months appeared in previous training data, so these are additional chronological diagnostics, not a newly independent external benchmark.

## Hypothesis and scope

C5 independently observed a meaningful weakness: on the second December fold, wind≥8m/s, rawMLP RMSE and positive bias exceed the curve. Test exactly one change: shrink the learned neural residual toward the empirical curve. For each seed, select epochs with the existing inner14-day stopping rule, reconstruct that inner-fit model at its selected epoch, then fit a single scalar alpha=clip(dot(residual_prediction, actual-minus-curve)/dot(residual_prediction,residual_prediction),0,1) on the inner stopping rows. Zero residual energy gives alpha0. Reinitialize/refit on outer training data; apply that fixed alpha to its neural correction. No outer labels, January labels, wind-specific alpha search or hyperparameter search.

Same immutable private NPZ SHA256 b4d01f11d33d485c1a36940b849ba345300698fa306ac98ffcb25749d5458dc0. Same7features, ResidualMLP architecture, optimizer and stopping config as V3; seeds42/137/2026 averaged equally. No newly sourced datasets, future SCADA lags, arbitrary clipping or larger network.

## Evaluation

Six expanding outer folds (issue≥start, target<end, training target<start): March1–April1, June1–July1, September1–October1, November1–December1, December1–15, December15–January1, all2025. Innerfit target<start−14days; stopping issue≥start−14days and target<start. Same rows for every method. Primary score unweighted mean of six foldRMSEs, separately for each turbine.

Methods: full-history curve, recent91-day curve, fixed CatBoostdepth4/400iterations/lr.04/seed42, raw3seedMLP, calibrated3seedMLP. The recent91-day curve is a drift reference and reproduces V1's approximate production history length; it is not claimed to reproduce the original V1 validation fits. CatBoost runs on GPU, whose numerical procedure can differ from CPU.

MAE/RMSE/bias and counts for each fold, each lead1–24/25–48, wind<4/4–8/≥8m/s, direction quadrants, belowzero temperature, actual low/high power using outer-training10th/90th percentiles, and actual absolute one-hour ramps≥outer-training90th percentile. Actual-based slices are evaluation only. Repeated targets across origins stay grouped for uncertainty. Low-count slices (<100pairs) are descriptive, ineligible for a strong conclusion. Unique target-hour means are also scored so duplicated horizons are visible.

Promotion of calibratedMLP requires, for BOTH turbines: completed6folds×3seeds; ≥2% meanRMSE improvement against BOTH curves and fixedCatBoost; no fold>5% RMSE regression against fullcurve; lead and highwind slices with≥100pairs no>5% regression; absolute bias no greater than fullcurve+0.01 overall. Require negative upper endpoint of descriptive paired3-dayblock95% delta interval vsfullcurve. These thresholds are our conservative engineering gates, not industry-standard or external-bigtech benchmarks. Even passing reused-data gates does not establish independent statistical significance. Otherwise retainV1; no relaxing thresholds after results.

Synthetic tests cover temporal leakage isolation, corrupted/nonfinite inputs, artifact integrity, deterministic inference, unsupported model/requests, weather availability/cutoff, missing and duplicate timestamps, full-horizon failure, extreme/weather-support inputs and orchestration failure. Synthetic success is reliability evidence, not real-world accuracy. Integration/API contract remains stable. Save code/data/weight/prediction hashes and actualCUDAdevice/version/runtime.

One run; do not rerun to select a favorable seed/device. A failure can be fixed and rerun only with explicit defect documentation. Hard training deadline16:20, report16:30, GPUstop16:40. CurrentV1 stays available; final production refit and adapter would follow only if the gate passes.

Skill: local theneoai-data-scientist/SKILL.md for preregistration, temporalvalidation and uncertainty (no persona credentials adopted). Official methodology references checked: https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split and https://docs.pytorch.org/docs/stable/notes/randomness.html. Historical weather availability +9h remains inferred; SCADA fixedUTC+6 unconfirmed; no Februarylabels.
