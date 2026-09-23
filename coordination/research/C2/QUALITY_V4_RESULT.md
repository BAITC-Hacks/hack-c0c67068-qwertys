# V4 result: calibrated DL improves point scores, fails promotion gates

Completed on NVIDIA TeslaT4/CUDA in107.970s. Six chronological periods across spring, summer, autumn and December, both turbines, three fixed neural seeds. Exactly36outer neural weights and12CatBoost models; noJanuary labels or additional dataset. The only new model change is inner-window residual shrinkage. Protocol dcb7c13, independent C5 pre-run tightening87de433 (timestamp correctiondacb354); no threshold relaxed after results.

| Mean six-fold RMSE | Turbine1 | Turbine2 |
|---|---:|---:|
| Full-history empirical curve | 0.255378 | 0.253685 |
| Recent91-day curve | 0.256619 | 0.255932 |
| Fixed GPU CatBoostdepth4 | 0.250428 | 0.256036 |
| Three-seed residualMLP | 0.249764 | 0.249698 |
| Same MLP with inner-fitted shrinkage | **0.248898** | **0.249107** |

Calibrated point improvement over fullcurve is2.54%/1.80%. This does not pass the frozen conservative gates. Turbine1 does not improve2% over CatBoost, regresses in December highwind and bias; turbine2 does not improve2% over fullcurve and regresses in March highwind/bias plus some other bias comparisons. Both descriptive95% paired3-target-day block intervals include zero (T1[-.012537,.000101],T2[-.010126,.001504]). These are retrospective reused-data diagnostics, not external industry benchmarks or a new independent test.

Decision: **retain productionV1 `nwp-tabular-7f1b4f31e9bb`**. V4 is research-only. No new production weights or API schema; C4 retains existing MODEL_DIR. No further search, threshold relaxation, favorable-seed selection or larger-model run. This decision is consistent with C5 independent recommendation and C3 acceptance. A high benchmark is an acceptance criterion, not a result we can assert in advance.

Local verification:12CSV files,13842rows,820slice/methodmetric cells,36DLweights and12CatBoost artifacts verified. Dataset/code/weight/prediction SHA match; target and issue alignment match immutableNPZ; zeroJanuary rows; scalers/curves use outertraining only; all seed means and shrinkage relations checked. CatBoost saved-model predictions reproduce exactly on CPU; neural saved-model CPU-vsCUDA maximum difference1.416e-7. Gate and block intervals recomputed exactly. See quality-v4-verification.json; full metrics including direction, temperature, power and ramp slices in evaluation-quality-v4.json. Synthetic reliability tests are reported separately, never added to accuracy metrics.

Private archive `artifacts/dl-v4/hackalem-quality-v4-results.zip`,5707082bytes, SHA256 `908498c58a3c41d913a0258565e5f3c507200a2da5bd031373668de5cea3b67e`. Checkpoints are evaluation-only. Input privacy, weather +9h inferred historical availability, unconfirmed SCADA fixedUTC+6 and absent Februarylabels remain unchanged.

Reproduction (authorized private440-run snapshot; use a fresh output directory and an explicit future UTC deadline):

```powershell
python -m src.ml.gpu_compare --prepare --scada-dir <complete-hour-scada> --weather-dir <immutable-440-run-weather> --dataset artifacts/quality-input/pairs.npz
$env:CUBLAS_WORKSPACE_CONFIG=":4096:8"
python -m src.ml.quality_cycle --dataset artifacts/quality-input/pairs.npz --output-dir artifacts/quality-reproduction --device cuda --deadline <UTC-ISO-hard-stop>
python -m pytest tests -q
```

PyTorch2.14.0+cu126, CatBoost1.2.10, NumPy2.5.3, Python3.12.14 on thisGPU. CPU execution is supported, but platform changes need not reproduce CUDA fitting bitwise. Installing CUDA dependencies belongs only to this optional research environment; productionV1 inference does not requireGPU orPyTorch.
