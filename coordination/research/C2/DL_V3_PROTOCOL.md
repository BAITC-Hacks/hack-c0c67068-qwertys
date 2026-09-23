# DL V3 — protocol frozen before neural results

23 September 2026, 15:18 UTC+5. Explicit user request: carefully evaluate ML/DL and NVIDIA. This is additional **post-test research**, not a new independent final test. V1 production remains unchanged. January has already been viewed in V1/V2; V3 will not inspect January labels or select using them.

Input: immutable V2 snapshot of 440 NWP runs, snapshot SHA256 `37f6e9e1b362d8530b76f37675aea415291fa508e57b6487ce786f95773af43a`. Same seven features, complete SCADA hours, both turbines, equal weight per issue/target pair. Duplicate target hours across origins are retained and explicitly counted. No February observed lags or labels.

Two outer folds: fit targets before 2025-12-01, evaluate origins from Dec 1 and targets before Dec 15; fit targets before Dec 15, evaluate origins from Dec 15 and targets before Jan 1. Within each training fold, last 14 days form the early-stopping interval: fitting targets strictly before that interval, validation origins on/after its start and targets before outer cutoff. Scaling and wind-curve calibration are fitted on fitting rows only. After choosing epoch count internally, refit on all outer training rows for exactly that many epochs.

Fixed candidates, no hyperparameter search:

* Residual MLP: width 64, three residual blocks with two linear layers each, GELU, LayerNorm, dropout 0.1; eight linear layers including input/output. Predict correction to training-fitted empirical wind curve.
* Feature-attention Transformer: seven numerical feature tokens plus CLS, token width 32, three pre-normalized Transformer layers, four heads, feed-forward width 64, dropout 0.1; predicts correction to the same curve. Inspired by FT-Transformer, **not an exact reproduction of its reference implementation** and not a temporal-history Transformer.
* AdamW, learning rate 0.001, weight decay 0.001, MSE loss, batch 512, gradient norm cap 1, maximum 60 epochs, patience 8 with minimum RMSE improvement 0.0001. Seeds 42, 137, 2026; average all three predictions, never select a favorable seed. CPU four threads; CUDA only if actually available/authorized.

Compare mean outer-fold RMSE against the unchanged V2 curve and fixed CatBoost results on identical rows. Report MAE, bias, lead 1–24/25–48 metrics, train/validation gap, per-seed variation, counts, input/code/weight hashes, runtime, actual device and package versions. Preserve prediction-level evidence privately. No arbitrary power clipping. A family is eligible only when both folds and all three seeds finish for that turbine. No automatic production replacement.

Hard stop 15:38 UTC+5 for training, 15:40 for report; incomplete cells stay explicitly incomplete. Do not delay UI/API acceptance. NVIDIA T4 is prepared but not deployed while explicit AWS personal/deployment data-sharing consent is pending. CPU training is not labeled NVIDIA training.

Sources checked 23 September 2026:

* https://arxiv.org/abs/2106.11959 — residual networks and feature Transformers are credible tabular DL comparisons; no universally superior model.
* https://arxiv.org/abs/2205.13504 — strong simple baselines matter for forecasting; this paper is not evidence that our particular Transformer will win or lose.
* https://docs.pytorch.org/docs/stable/generated/torch.optim.AdamW.html — optimizer API.
* https://docs.pytorch.org/docs/stable/notes/randomness.html — determinism is platform/version dependent.
* https://catboost.ai/docs/en/features/training-on-gpu — GPU training exists and may be nondeterministic; GPU is not an accuracy guarantee.

Historical weather availability remains conditional (`run+9h` inferred, provenance unconfirmed); SCADA fixed UTC+6 remains a hypothesis. December folds were used before, so repeated research may overfit them. This experiment can support engineering comparison, not a fresh generalization claim.
