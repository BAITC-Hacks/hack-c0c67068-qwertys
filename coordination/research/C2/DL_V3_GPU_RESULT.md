# Actual NVIDIA T4 training — V3 completed

Remote report: completed, CUDA, TeslaT4, PyTorch2.14.0+cu126,115.418441373s. The same frozen procedure on the local CPU took614.75s (observed runtime ratio5.33; early-stopping epochs differ across devices, so this is not a controlled equal-work hardware benchmark). GPU run was performed on the private project NPZ, not a generic CUDA smoke test.

| Mean two-fold RMSE | Turbine1 | Turbine2 |
|---|---:|---:|
| Curve, extendedhistory | .2667663853 | .2679536149 |
| Fixed CatBoostdepth4 CPU reference | .2629482401 | .2662616076 |
| GPU residualMLP, three-seedmean | .2609733245 | .2650565332 |
| GPU featureTransformer, three-seedmean | .2617989175 | .2633687273 |

All four paired3-target-day block95% intervals versus curve include zero. These December folds were reused; numerical point gains do not establish robust independent improvement. CPU/GPU fitted parameters and early-stop epochs differ; no best-device or best-seed reselection. The productionV1 model remains unchanged.

Downloaded archive2726367bytes SHA256 `4f804e9d6f062f500e359a80c4d56c4a76ab565fda397474cebd8b447292a409`. Local verification checked24weightSHA,8predictionCSV SHA, ensemble arithmetic, metrics, all5496predictionrows, exactlyzeroJanuaryrows. Dataset and trainingcode hashes match uploaded local inputs. All24weights load on CPU and return finite predictions. Maximum saved-model CPU versus recorded CUDA inference difference is0.000034362077713; these are numerically close, not bitwise identical. An initial2e-6 cross-device equality check failed; it was replaced by transparent measurement rather than a false exact-reproduction claim. Same-device verification is separate.

Public evidence: evaluation-dl-v3-gpu.json, dl-v3-gpu-summary.json, gpu-v3-verification.json. Raw labels, predictions and weights remain private under artifacts/dl-v3/gpu-export/gpu-results. These are evaluation-fold checkpoints, not a deployable production refit.

The first Brev startup script failed (systemPython3.10 lackedensurepip); a separate uvPython3.12 environment was successfully installed and used. Browser setup status reflects the initial failed script, not the subsequently completed training. After the separately authorized V4 cycle, the provider confirmed compute Stopped at16:05:12 UTC+5. Disk remains $0.02/hour pending specific deletion confirmation; see the resource ledger. Historical weather availability and SCADA timezone remain inferred.

Follow-up on the same Tesla T4 restored all24 saved checkpoints and measured maximum absolute difference **0.0** against their recorded CUDA predictions. Downloaded93-byte JSON SHA256 `13d5ba68ccc437089aa64926c26ee2e219546ce62f0eb005ea170ad870f53391`; public copy gpu-v3-same-device-restore.json. This is a C2 measurement, not a separate C5 CUDA run; the compact JSON does not contain per-checkpoint hashes. Full weight identity is checked by the archive/export verification. The previously disclosed CPU/CUDA discrepancy remains valid.
