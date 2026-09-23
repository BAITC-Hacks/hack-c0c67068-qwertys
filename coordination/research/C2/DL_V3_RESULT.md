# DL V3 CPU comparison completed

Completed23 September2026 around15:30 UTC+5, before15:38 hard stop. Full experiment614.75s CPU. Two neural families × two turbines × two outer folds × three seeds =24 saved outer-fold models, each with a separate inner early-stopping run. Residual MLP26,049 parameters; feature Transformer26,209. Training plus inner validation/refit took69.92s for MLP and542.22s for Transformer. No January targets used by this experiment.

Lower is better; mean RMSE of the same two December outer folds in original normalized_power units:

| Model | Turbine1 | Turbine2 |
|---|---:|---:|
| V2 NWP wind curve |0.26676639|0.26795361|
| V2 fixed CatBoost depth4 |0.26294824|0.26626161|
| Residual MLP, three-seed mean |**0.26131337**|**0.26445546**|
| Feature Transformer, three-seed mean |0.26430615|0.26461895|

Residual MLP improves the point estimate over CatBoost by0.62%/0.68%, and over the curve by2.04%/1.31%. This is **not a demonstrated robust or independent generalization improvement**. Descriptive95% paired3-day-block intervals for mean-fold RMSE difference MLP-minus-curve are[-0.02388,+0.01482] and[-0.01991,+0.01495], both include zero. December folds were already reused in earlier work. Transformer is slower here and does not outperform MLP on either turbine. More depth did not automatically help.

Outer validation row counts match V2 exactly: T1 614/766; T2 602/766. Recomputed baseline errors match V2 to1e-12. No raw future SCADA, February labels, random train/test split or arbitrary output clipping. Standardization and calibration fit on training only; inner early stopping includes an origin/target boundary guard; all three seeds are averaged. Train/outer-validation errors and per-seed spread are in evaluation-dl-v3.json, with code/input/weight/prediction hashes and every stopping history.

Decision: preserve V1 production and publish this as optional post-test research. No further tuning or claim that neural evaluation weights are production-ready. Promotion requires an explicit integration decision and production refit/inference acceptance; MODEL_DIR is unchanged. GPU reproduction is a separate actual-device check and does not create a new untouched test.

Artifacts: evaluation-dl-v3.json, dl-v3-summary.json, DL_V3_PROTOCOL.md, DL_REPRODUCE.md. Private artifacts/dl-v3/results holds24.pt checkpoints and8prediction CSVs; no secrets or raw data committed. Full local suite38PASS, including three optional DL tests; same-row baseline equivalence and prediction evidence checked by deep_report.

Source interpretation: residual networks and feature-attention models are credible tabular baselines ([Gorishniy et al.](https://arxiv.org/abs/2106.11959)); our compact attention network is inspired by that family, not an exact FT-Transformer reproduction. Empirical results above, not architecture names, determine the conclusion.

Persistent limitations: SCADA UTC+6 assumption, inferred NWP publication gate+9h with unconfirmed historical availability, no February labels. These do not disappear with DL or NVIDIA.
