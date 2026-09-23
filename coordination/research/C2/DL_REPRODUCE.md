# Optional neural experiment reproduction

The production forecast API does not import PyTorch. `src.ml.deep_compare` is an optional research entry point; installing its dependencies does not change the selected production model. Source protocol: DL_V3_PROTOCOL.md, committed44a845a before neural results. Initial implementation b05bc81.

CPU environment actually used: Python3.12.14, PyTorch2.14.0+cpu from the official wheel index, NumPy2.5.3. Install optional dependency into the existing project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install torch==2.14.0 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pytest tests/test_deep_compare.py -q
.\.venv\Scripts\python.exe -m src.ml.gpu_compare --prepare --scada-dir <C1-hourly-directory> --weather-dir <immutable-V2-weather-snapshot> --dataset artifacts/dl-v3/pairs.npz
.\.venv\Scripts\python.exe -m src.ml.deep_compare --dataset artifacts/dl-v3/pairs.npz --output-dir artifacts/dl-v3/results --device cpu --deadline <future-absolute-ISO-UTC-hard-stop>
.\.venv\Scripts\python.exe -m src.ml.deep_report --directory artifacts/dl-v3/results --comparison coordination/research/C2/evaluation-v2-posttest.json --destination artifacts/dl-v3/summary.json
```

The private NPZ contains the same joined V2 rows. `deep_compare` filters all January targets before any fitting/scoring operation. It fits a baseline curve and scaler separately on each legitimate training partition; the output neural network learns a correction to that curve. Early stopping selects epoch count only on an inner14-day chronological interval. A fresh model then refits on the entire outer training portion. Predictions from seeds42/137/2026 are averaged, never selected individually.

Each `.pt` checkpoint includes family, CPU state_dict, training-fitted scaling and curve, fit cutoff and seed. Use `torch.load(path, weights_only=True)` only on trusted project-generated artifacts; instantiate `make_model(family, seed, device)`, load the state_dict, standardize with the saved mean/scale and add `curve_predict(saved_curve, wind)` to the neural output. They are **outer-fold evaluation weights**, not production refits through January. No claim that setting MODEL_DIR to this folder enables the API: no production manifest/adapter has been promoted for these weights.

CUDA requires an actual supported driver/device. On the authorized one-machine Brev experiment, validate `nvidia-smi`, `torch.cuda.is_available()`, reported GPU name and a real forward/backward pass. Then run the same frozen comparison with `--device cuda` and `CUBLAS_WORKSPACE_CONFIG=:4096:8` in the process environment. The absolute hard stop is mandatory. Record actual package/device versions; equality across CPU/GPU/platform versions is not promised. No automatic CPU fallback when CUDA was requested.

`deep_report` verifies identical validation counts and baseline RMSE against V2 to1e-12 before comparing families. Its 3-day paired circular block bootstrap keeps overlapping forecasts for the same target day together; intervals are descriptive only, because the December folds have been reused and model families compared. January/February metrics are not fabricated.

Original weather source publication time and SCADA UTC+6 remain unconfirmed assumptions. This limitation survives any architecture or hardware choice.
