# Deep learning & time-series foundation models for NWP-driven day-ahead (24–48 h) wind power forecasting — hackathon usability compendium (as of 2026-09-23)

Context used only for relevance: 2 turbines (KZ), hourly, ~25k samples/turbine, future-known NWP covariates (wind speed/dir/temp at several heights), power ACF ≈ 0.1 at lag 24 h → the task is essentially a nonlinear, near-instantaneous NWP→power regression, not a pattern-extrapolation task. Windows laptop, CPU, 4 h.

Legend: **F** = future-known exogenous (NWP forecasts), **H** = historical/past-only exogenous, **S** = static.

---

## Q1. Supervised deep models (N-BEATS/x, N-HiTS, TFT, PatchTST, TimesNet, iTransformer, TiDE, TSMixer/x, DLinear/NLinear, LSTM/GRU/TCN, KDD Cup 2022 graph models): covariate support, wind evidence, DL vs GBM

### Takeaway
Only a subset of popular DL forecasters accept future-known covariates (TFT, TiDE, NBEATSx, NHITS, TSMixerx, LSTM/GRU/TCN/BiTCN, DeepAR in neuralforecast; PatchTST, iTransformer, NBEATS, NLinear, TSMixer do **not** in neuralforecast), and wind-specific day-ahead studies from 2024–2026 repeatedly find that history-driven sequence models underperform while GBMs (LightGBM/XGBoost) and power-curve/physics approaches remain strong baselines; on ~25k-row tabular-like NWP→power data, the literature gives no reason to expect a from-scratch deep model to beat a tuned GBM within a 4-hour CPU budget.

### Cited Findings

**Covariate support (neuralforecast v3.x capability table)**
- neuralforecast capability table (F/H/S = future/historical/static exog): TFT F/H/S; TiDE F/H/S; NBEATSx F/H/S; NHITS F/H/S; TSMixerx F/H/S (multivariate); BiTCN F/H/S; TCN F/H/S; LSTM/GRU/RNN F/H/S (recursive or direct via `recursive=False`); DilatedRNN F/H/S; DeepAR F/S; MLP F/H/S; KAN F/H/S; xLSTM F/H/S; XLinear F/H/S; DeepNPTS F/H/S; TimesNet F only; Autoformer/FEDformer/Informer/VanillaTransformer F only; TimeXer H/S only (no future exog); **NBEATS, NLinear, PatchTST, iTransformer, TSMixer, TimeMixer, SOFTS, StemGNN, TimeLLM: no exog** — [neuralforecast capabilities overview](https://nixtlaverse.nixtla.io/neuralforecast/docs/capabilities/overview.html)
- AutoGluon-TimeSeries DL models (GluonTS-backed): known covariates supported only by DeepAR, TemporalFusionTransformer, TiDE; past covariates by TFT and TiDE; DLinear, PatchTST, SimpleFeedForward, WaveNet have no covariate support there — [AutoGluon model zoo](https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-model-zoo.html)
- Darts: future covariates supported by regression models (LightGBMModel, CatBoostModel, XGBModel, LinearRegressionModel, SKLearnModel), and by TFTModel, TiDEModel, TSMixerModel, DLinearModel, NLinearModel (Darts versions of DLinear/NLinear accept covariates, unlike neuralforecast's), plus a `NeuralForecastModel` wrapper — [Darts README model table](https://github.com/unit8co/darts); TFT in Darts requires future covariates (or auto-generated encoders via `add_encoders`) — [Darts TFT docs](https://unit8co.github.io/darts/generated_api/darts.models.forecasting.tft_model.html); covariate concepts — [Darts covariates guide](https://unit8co.github.io/darts/userguide/covariates.html)
- TFT architecture: static covariate encoders, variable-selection networks, gating, explicit handling of known-future inputs and observed inputs, quantile outputs — [Lim et al., TFT, arXiv 1912.09363](https://arxiv.org/abs/1912.09363)
- NBEATSx extends N-BEATS with exogenous variables; evaluated on electricity price forecasting (EPF) where day-ahead load/renewable forecasts are the exogenous inputs; reported ~20% accuracy gain vs original N-BEATS and up to ~5% vs specialized EPF statistical/ML methods — [Olivares et al., NBEATSx, arXiv 2104.05522](https://arxiv.org/abs/2104.05522). Original N-BEATS (univariate) — [arXiv 1905.10437](https://arxiv.org/abs/1905.10437); N-HiTS (hierarchical interpolation, long horizons) — [arXiv 2201.12886](https://arxiv.org/abs/2201.12886)
- TiDE: MLP encoder–decoder designed to handle covariates and non-linear dependencies; claimed to match/beat Transformer LTSF models while being 5–10× faster — [Das et al., TiDE, arXiv 2304.08424](https://arxiv.org/abs/2304.08424)
- TSMixer: all-MLP mixer; the extended variant (TSMixer-Ext) ingests static and future time-varying features, evaluated on M5 — [Chen et al., TSMixer, arXiv 2303.06053](https://arxiv.org/abs/2303.06053)
- PatchTST (channel-independent patching, univariate-per-channel, no exog in original design) — [arXiv 2211.14730](https://arxiv.org/abs/2211.14730); iTransformer (variates-as-tokens, multivariate) — [arXiv 2310.06625](https://arxiv.org/abs/2310.06625); TimesNet (2D-variation CNN) — [arXiv 2210.02186](https://arxiv.org/abs/2210.02186); TimeXer (endogenous + exogenous tokens) — [arXiv 2402.19072](https://arxiv.org/abs/2402.19072)

**Evidence on wind / energy**
- UniWind (Jul 2026, 24 wind farms: 22 Chinese + UK Kelmarsh & Penmanshiel, 15-min, day-ahead from NWP) compared PowerCurve, LightGBM, XGBoost, PatchTST, iTransformer, TimeMixer, xPatch, CrossViViT, FusionSF, 2DXformer and foundation models (WindFM, Chronos-2, Moirai, Moirai-PT). Authors state that "time series forecasting models that rely on historical sequence patterns generally underperform"; LightGBM/XGBoost are "strong practical baselines" but less stable across regions; their physics-informed model (monotonic power-curve prior + state-aware corrector) wins (e.g., SD_A MAE 12.05 vs next-best FusionSF 25.37) — [UniWind, arXiv 2607.01670](https://arxiv.org/html/2607.01670)
- Meisenbacher et al. (Nov 2024): for day-ahead wind power with weather forecasts, power-curve-modelling approaches achieved lower errors than three autoregressive DL methods, needed less data cleaning, and were computationally cheaper; autoregressive models are hurt by irregular (redispatch) shutdowns in the power history — [arXiv 2412.00423](https://arxiv.org/abs/2412.00423)
- ERCOT/ARPA-E PERFORM study (Apr 2026, wind/solar/load): with 100% data fine-tuning, wind nMAE: TimesFM 3.84%, Chronos-Bolt 3.91%, TimeXer 4.01%, TFT 4.08%, Moirai-L 4.17%, PatchTST 4.33%, MOMENT 4.33%, TTM 4.86%, 1D-CNN 6.51%, LSTM 6.85%; adding weather inputs improved e.g. Moirai-L 4.17%→3.78%; zero-shot (no fine-tune) wind nMAE was 8.7–12.1%; GPU: 2×A100; **no GBM baseline** — [Za'ter & Hodge, arXiv 2604.22077](https://arxiv.org/html/2604.22077)
- KDD Cup 2022 SDWPF (Baidu): 134 turbines, ~half-year of 10-min SCADA incl. turbine positions and internal status; >2,400 registered teams — [SDWPF dataset paper, arXiv 2208.04360](https://arxiv.org/abs/2208.04360). Team 88VIP ensembled a GBDT ("to memorize the basic data patterns") with an RNN/GRU, with sub-models for different timescales, plus feature engineering/imputation/offline-eval design — [88VIP, arXiv 2208.08952](https://arxiv.org/abs/2208.08952). Spatio-temporal GNN approach — [BUAA_BIGSCity, arXiv 2302.11159](https://arxiv.org/pdf/2302.11159); another solution repo — [shaido987/KDD_wind_power_forecast](https://github.com/shaido987/KDD_wind_power_forecast)
- fev-bench includes a wind-power task derived from the KDD Cup 2022 dataset — [fev-bench paper](https://arxiv.org/html/2509.26468v4)

**DL vs GBM / linear baselines (general)**
- "Are Transformers Effective for TS Forecasting?": a one-layer linear model (DLinear/NLinear) beat sophisticated Transformer LTSF models on 9 benchmarks, often by large margins — [Zeng et al., arXiv 2205.13504](https://arxiv.org/abs/2205.13504)
- Tree-based models remained SOTA on medium-sized tabular data (~10k samples) across 45 datasets — [Grinsztajn et al., NeurIPS 2022, arXiv 2207.08815](https://arxiv.org/abs/2207.08815)
- TabArena (2025 living benchmark, 51 datasets, 25M runs): GBDTs still strong; top DL models reach parity only with extensive tuning + post-hoc ensembling; tabular foundation models (TabPFNv2) dominate small datasets (≤10k rows); a diverse ensemble beats every single model — [TabArena, arXiv 2506.16791](https://arxiv.org/abs/2506.16791)
- M5 competition: top solutions were dominated by LightGBM-based global models — [Makridakis et al., IJF 2022](https://doi.org/10.1016/j.ijforecast.2021.11.013)

### Inferences
- Because ACF(24 h) ≈ 0.1, architectures whose strength is extrapolating the target's own history (PatchTST, iTransformer, NBEATS, NLinear/DLinear-without-exog, TimesNet, TSMixer without "x") are structurally mismatched to this task; if a DL model is tried, it must be one with **F** support (TFT, TiDE, NHITS/NBEATSx with `futr_exog_list`, TSMixerx, BiTCN, or a plain MLP on NWP features).
- For ~25k rows × tens of NWP features, the task is effectively tabular; TabArena/Grinsztajn suggest a tuned GBM is the reference and a from-scratch DL model will likely need ensembling/tuning time that a 4-h CPU hackathon does not have. A small MLP/TiDE is cheap enough on CPU to try as an ensemble member rather than as the primary model.
- KDD Cup 2022 lessons transfer only partly: SDWPF had no NWP forecasts (only SCADA history — see Gaps), so its winners relied on history; the robust transferable lesson is "GBDT + NN ensemble", not graph models (only 2 turbines here, so spatial GNNs add nothing).

### Gaps
- No verified side-by-side benchmark on a public **NWP-driven, single-turbine, hourly, 24–48 h** dataset with LightGBM vs TFT/TiDE/NHITS vs Chronos-2/TabPFN-TS under equal tuning budgets was found.
- UniWind full per-dataset LightGBM vs PatchTST numbers were not extracted (only the aggregate statements and UniWind vs FusionSF examples).
- Whether SDWPF contained forecast (vs observed) weather was not re-verified from the full dataset paper; the abstract describes SCADA/"dynamic context" only.
- DLinear inclusion in the neuralforecast capability table was not visible in the fetched table (NLinear appears with no exog).

---

## Q2. Time-series foundation models (TSFMs) as of Sept 2026: licence, size, CPU, pip, covariates, benchmarks, API keys

### Takeaway
The 2026 frontier on covariate-aware zero-shot forecasting is **Chronos-2 (Apache-2.0, 120M/28M, `chronos-forecasting`, native past+future covariates)**, **TiRex-2 (Apache-2.0, 38–82M, `tirex-2`, native past+future covariates, Jul 2026)**, **TimesFM-3 (330M, native covariates, Aug 2026, but NON-COMMERCIAL weights)** and **TabPFN-TS (known-future covariates as tabular regression; strongest on instantaneous target–covariate relations, but TabPFN-3 weights are non-commercial and CPU-slow; default backend is a cloud API)**; univariate-only TSFMs (Chronos-Bolt, Moirai 2.0, Toto 2.0, Sundial, Lag-Llama, TimesFM-2.5 without XReg) cannot exploit NWP and are near-useless when ACF(24 h)≈0.1.

### Cited Findings

**Leaderboards (state as of Sept 2026)**
- fev-bench: 100 tasks from 96 datasets, 7 domains; 46 tasks with covariates (30 known-dynamic, 24 past-dynamic, 19 static); 26 energy tasks (EPF with load/renewable forecasts as covariates, ERCOT, ENTSO-e load, solar with weather covariates, KDD Cup wind). In the paper, only Chronos-2 (past+known) and TabPFN-TS (known only) natively used covariates; on 42 dynamic-covariate tasks, skill score with vs without covariates: Chronos-2 47.0% vs 40.9%, TabPFN-TS 42.5% vs 34.1%; Chronos-2 runtime ≈0.8 s per 100 series vs 146.9 s for the SCUM statistical ensemble — [fev-bench, arXiv 2509.26468](https://arxiv.org/html/2509.26468v4)
- fev-bench leaderboard mirror (aggregator, auto-refreshed from upstream; verify on official): 1 TimesFM-3 (skill 37.42), 2 Chronos-2 (35.50), 3 t0-beta (34.86), 4 TiRex-2 (33.74), 5 Toto-2.0-2.5B (32.54), 6 Toto-2.0-1B, 7 Toto-2.0-313m, 8 TS-ICL, 9 Toto-2.0-22m, 10 TabPFN-TS-3 (30.56; normalized runtime 234.6 s vs Chronos-2 0.84 s), 11 TimesFM-2.5 (30.20), 12 TiRex (30.01), 13 TabPFN-TS, 15 Toto-1.0, 17 FlowState (IBM), 18 Moirai-2.0 (27.22), 19 Chronos-Bolt (26.52), 20 Sundial-Base (24.75) — [tsfm.ai fev-bench mirror](https://tsfm.ai/benchmarks/fev-bench)
- GIFT-Eval (23 datasets, 144k series, 97 task configs, 7 domains, 10 frequencies) — [GIFT-Eval paper](https://arxiv.org/abs/2410.10393); official leaderboard — [HF Space Salesforce/GIFT-Eval](https://huggingface.co/spaces/Salesforce/GIFT-Eval); repo — [SalesforceAIResearch/gift-eval](https://github.com/SalesforceAIResearch/gift-eval). As of 2026-09-22 the top-12 is dominated by agentic/ensemble submissions (STRIDE w/ Synapse, EXAONE-Forecast-Agent, LS-MoE, …); TimesFM-3 is the best single model at rank 13 (MASE 0.67, CRPS 0.46), Toto-2.0-FnF rank 15 — [tsfm.ai GIFT-Eval mirror](https://tsfm.ai/benchmarks/gift-eval). GIFT-Eval is essentially univariate/no-known-covariate, so it says little about NWP-driven tasks.

**Amazon Chronos family**
- Chronos-2 (released 20 Oct 2025): encoder-only, group attention for ICL across target + covariates, 120M params (plus 28M `chronos-2-small`, ~2× faster, "suitable for CPU-only"), context up to 8,192, horizon up to 1,024, 21 quantiles (0.01–0.99), real + categorical past and future covariates natively, zero-shot; SOTA on fev-bench, GIFT-Eval, Chronos Benchmark II with largest gains on covariate tasks; on 16 fev-bench energy tasks with covariates it beat TabPFN-TS and TiRex — [Chronos-2 paper](https://arxiv.org/html/2510.15821), [HF amazon/chronos-2](https://huggingface.co/amazon/chronos-2), [Amazon Science blog](https://www.amazon.science/blog/introducing-chronos-2-from-univariate-to-universal-forecasting)
- Licence Apache-2.0; `pip install chronos-forecasting`; API `Chronos2Pipeline.from_pretrained("amazon/chronos-2").predict_df(context_df, future_df=future_df, prediction_length=24, quantile_levels=[0.1,0.5,0.9])` — [HF amazon/chronos-2](https://huggingface.co/amazon/chronos-2)
- Chronos-Bolt (Nov 2024; 9M–205M; "up to 250× faster, 20× more memory-efficient" than original Chronos; univariate — covariates only through an external regressor) and original Chronos (8M–710M) are effectively superseded by Chronos-2 — [chronos-forecasting GitHub](https://github.com/amazon-science/chronos-forecasting)
- In AutoGluon: `hyperparameters={"Chronos2": {...}}`, model paths `autogluon/chronos-2` and `autogluon/chronos-2-small`, `fine_tune=True` optional (recommended mainly with >100 series and history > 3×horizon), `known_covariates_names=[...]`, presets `chronos2`, `chronos2_small`, `chronos2_ensemble`; Chronos-Bolt can use a CatBoost/LightGBM "covariate regressor" — [AutoGluon Chronos-2 tutorial](https://auto.gluon.ai/dev/tutorials/timeseries/forecasting-chronos.html)

**Google TimesFM**
- TimesFM-2.5 (15 Sep 2025): 200M params (down from 500M in 2.0), context up to 16k, optional 30M quantile head, horizons up to 1k, weights Apache-2.0; `pip install timesfm[torch]` — [TimesFM GitHub](https://github.com/google-research/timesfm)
- TimesFM-2.5 covariates via **XReg** (Oct 2025): `forecast_with_covariates(dynamic_numerical_covariates=..., dynamic_categorical_covariates=..., static_categorical_covariates=..., xreg_mode="xreg + timesfm" | "timesfm + xreg")`; requires `pip install timesfm[xreg]` (pulls scikit-learn + JAX); future covariates must cover context + full horizon; CPU guidance: `per_core_batch_size=8` for 8 GB RAM — [TimesFM SKILL.md](https://github.com/google-research/timesfm/blob/master/timesfm-forecasting/SKILL.md). XReg = ridge regression on covariates combined with TimesFM (one mode fits regression then TimesFM on residuals; the other the reverse) — [Darts issue #2976](https://github.com/unit8co/darts/issues/2976)
- TimesFM-3 (31 Aug 2026): 330M, first natively multivariate TimesFM; accepts multiple targets, past covariates and past-future covariates (explicitly including weather forecasts) zero-shot; #1 among pretrained models on fev-bench and best average rank on GIFT-Eval per Google; HF id `google/timesfm-3.0-pytorch`; **weights under `timesfm-non-commercial-license-v1.0` — non-commercial, non-production use only** (code Apache-2.0) — [Google Research blog](https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/), [TimesFM GitHub](https://github.com/google-research/timesfm), [MarkTechPost](https://www.marktechpost.com/2026/08/31/google-ai-releases-timesfm-3-a-330m-parameter-zero-shot-foundation-model-for-multivariate-time-series-forecasting/)
- TimesFM 1.0/2.0 archived under `v1/` (`pip install timesfm==1.3.0`) — superseded — [TimesFM GitHub](https://github.com/google-research/timesfm)

**NX-AI TiRex / TiRex-2**
- TiRex-2 (1 Jul 2026): xLSTM-based; 38.4M params univariate + 44.1M for multivariate (82.5M); single checkpoint, zero-shot, streaming; natively conditions on past and future-known covariates via bidirectional time mixer + grouped-attention variate mixer; Apache-2.0; `pip install tirex-2`; CPU works (`device="cpu"`); the fused CUDA sLSTM kernel ("FlashRNN") needs NVCC + compute capability ≥8.0 and, on Windows, Visual Studio Build Tools — CPU mode avoids this — [HF NX-AI/TiRex-2](https://huggingface.co/NX-AI/TiRex-2), [GitHub NX-AI/tirex-2](https://github.com/NX-AI/tirex-2), [arXiv 2607.01204](https://arxiv.org/pdf/2607.01204)
- TiRex v1 (univariate) — [GitHub NX-AI/tirex](https://github.com/NX-AI/tirex); superseded by TiRex-2 for covariate use.

**Salesforce Moirai**
- Moirai 2.0 (Aug 2025): decoder-only, quantile loss, multi-token prediction, trained on 36M series; 44% faster and 96% smaller than predecessor; e.g. `moirai-2.0-R-small` = 11.4M params; **licence CC-BY-NC-4.0**; install via cloning `uni2ts` (`pip install -e '.[notebook]'`); model card documents no covariate usage — [HF Salesforce/moirai-2.0-R-small](https://huggingface.co/Salesforce/moirai-2.0-R-small), [Salesforce blog](https://www.salesforce.com/blog/moirai-2-0/), [arXiv 2511.11698](https://arxiv.org/abs/2511.11698); Moirai-MoE — [Salesforce blog](https://www.salesforce.com/blog/time-series-morai-moe/). fev-bench mirror flags 28% training overlap for Moirai-2.0 — [tsfm.ai](https://tsfm.ai/benchmarks/fev-bench)

**Datadog Toto**
- Toto 2.0: five sizes (4m, 22m, 313m, 1B, 2.5B), Apache-2.0 weights+code; claimed SOTA on BOOM, GIFT-Eval and TIME; **exogenous-variable support and fine-tuning not yet available in 2.0 — use Toto 1.0 for those** — [Datadog Toto 2.0 blog](https://www.datadoghq.com/blog/ai/toto-2/), [HF Datadog/Toto-2.0-22m](https://huggingface.co/Datadog/Toto-2.0-22m), [GitHub datadog/toto](https://github.com/datadog/toto). AutoGluon ships `TotoModel` and `Toto2Model` — [AutoGluon model zoo](https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-model-zoo.html)

**Prior Labs TabPFN-TS**
- TabPFN-TS treats forecasting as tabular regression (TabPFN + calendar/sin-cos/running-index features); "univariate, target-history + known-future covariate regression"; past-dynamic and static covariates are dropped; original paper: 11M-param TabPFN-v2 backbone, SOTA on covariate-informed forecasting — [arXiv 2501.02945](https://arxiv.org/abs/2501.02945), [GitHub PriorLabs/tabpfn-time-series](https://github.com/PriorLabs/tabpfn-time-series)
- `pip install tabpfn-time-series` (v1.3.0, Sep 2026; needs `tabpfn>=9.0.0`, `tabpfn-client>=0.5.3`); **default backend is the cloud API via `tabpfn-client` (account/terms at ux.priorlabs.ai → data leaves the machine)**; local mode via `tabpfn` on GPU/CPU; package code Apache-2.0; default checkpoint TabPFN-3.5, finetuned TabPFN-TS-3 available — [GitHub PriorLabs/tabpfn-time-series](https://github.com/PriorLabs/tabpfn-time-series), [PyPI](https://pypi.org/project/tabpfn-time-series/)
- TabPFN-3 weights: "TABPFN-3.0 License v1.0" — research/internal evaluation allowed; no commercial/production use of model or outputs — [HF Prior-Labs/tabpfn_3](https://huggingface.co/Prior-Labs/tabpfn_3), [TabPFN-3 report arXiv 2605.13986](https://arxiv.org/abs/2605.13986)
- Controlled study (Berthelier et al., May 2026): TabPFN-TS captures simple **instantaneous** target–covariate relations (identity, additive, quadratic, composite) better than Chronos-2, especially at short horizons (e.g., composite relation MSE 0.0008–0.0013 vs 0.188–0.194 for Chronos-2); Chronos-2 improves relative to TabPFN-TS as lagged/autoregressive dependence grows; both struggle with very short contexts — [arXiv 2605.12200](https://arxiv.org/html/2605.12200v1)

**Other TSFMs**
- IBM TTM / granite-timeseries-ttm-r2: ~1M-param class ("starting from 1M"), Apache-2.0, `pip install granite-tsfm`, CPU/laptop-friendly; context/horizon configs 512/1024/1536 × 96–720; designed for 10-min/15-min/hourly; **exogenous/control variables and static categoricals only via fine-tuning ("exogenous infusion")**; r2 ≈15% better than r1 — [HF granite-timeseries-ttm-r2](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2)
- Sundial (THUML, ICML 2025 oral): 128M, pretrained on ~1T points, generative/probabilistic, Apache-2.0, `thuml/sundial-base-128m` — [HF](https://huggingface.co/thuml/sundial-base-128m), [GitHub](https://github.com/thuml/Sundial); Timer / Timer-XL checkpoint `thuml/timer-base-84m` — [HF](https://huggingface.co/thuml/timer-base-84m), [GitHub Large-Time-Series-Model](https://github.com/thuml/Large-Time-Series-Model); Sundial-Base ranks ~20 on fev-bench mirror — [tsfm.ai](https://tsfm.ai/benchmarks/fev-bench)
- TimeGPT (Nixtla, closed weights): requires API key from dashboard.nixtla.io; 30-day free trial, no card; enterprise plans otherwise; supports future exogenous (`X_df`) and fine-tuning via API; `pip install nixtla` — [TimeGPT subscription plans](https://www.nixtla.io/docs/introduction/timegpt_subscription_plans), [Nixtla quickstart](https://nixtlaverse.nixtla.io/nixtla/docs/getting-started/quickstart.html), [PyPI nixtla](https://pypi.org/project/nixtla/)
- Mitra (Amazon, 2025): **tabular** (not TS) foundation model, 72M-param 12-layer transformer, ICL on synthetic priors, Apache-2.0, CPU+GPU, in AutoGluon-Tabular; strongest on small tables (<5k rows, <100 features) — [Amazon Science blog](https://www.amazon.science/blog/mitra-mixed-synthetic-priors-for-enhancing-tabular-foundation-models), [HF autogluon/mitra-regressor](https://huggingface.co/autogluon/mitra-regressor), [AutoGluon tabular FMs](https://auto.gluon.ai/stable/tutorials/tabular/tabular-foundational-models.html)
- WindFM (Sep 2025): wind-specific generative FM, 8.1M params, tokenizer + decoder-only transformer, claims SOTA zero-shot deterministic & probabilistic wind forecasting and cross-continent OOD robustness; weights at [GitHub shiyu-coder/WindFM](https://github.com/shiyu-coder/WindFM) — [arXiv 2509.06311](https://arxiv.org/abs/2509.06311). In UniWind's day-ahead NWP benchmark, WindFM/Chronos-2/Moirai zero-shot were beaten by 29–62% MAE by the physics-informed UniWind — [arXiv 2607.01670](https://arxiv.org/html/2607.01670). Tyan-WP (2026) is an ultra-short-term wind FM (not day-ahead) — [arXiv 2606.08630](https://arxiv.org/pdf/2606.08630)
- Lag-Llama (ServiceNow, 2024, univariate probabilistic) — [GitHub](https://github.com/time-series-foundation-models/lag-llama); absent from the fev-bench top-20 mirror — superseded — [tsfm.ai](https://tsfm.ai/benchmarks/fev-bench)

**Energy-domain evidence for TSFMs**
- FETS benchmark (Apr/Jul 2026; 54 energy datasets, 9 categories): covariate-informed zero-shot Chronos-2 (median NRMSE 0.472) and TiRex-2 (0.474) beat task-trained XGBoost (0.611) and random forest (0.696) — [arXiv 2604.22328](https://arxiv.org/abs/2604.22328)
- EPF study (Jul 2026, ICML FMSD workshop): TSFM performance "depends critically on covariate support"; TSFMs do not consistently beat domain-specific EPF methods; simple ensembles of TSFMs + domain methods look promising — [Pan & Ezzat, arXiv 2607.02623](https://arxiv.org/abs/2607.02623)
- ERCOT wind: zero-shot TSFM nMAE 8.7–12.1% (TimesFM best) vs ~3.8–4.9% after fine-tuning on GPU — [arXiv 2604.22077](https://arxiv.org/html/2604.22077)
- Darts now wraps Chronos2Model, TimesFM2p5Model, TimesFM3Model, TiRexModel, PatchTSTFMModel (IBM) — [Darts README](https://github.com/unit8co/darts)

**Summary table (verified items only; "?" = not verified)**

| Model | Licence (weights) | Size | pip | Future-known covariates | CPU notes | API key |
|---|---|---|---|---|---|---|
| Chronos-2 | Apache-2.0 | 120M / 28M small | `chronos-forecasting` (also AutoGluon, Darts) | Native (real+categorical) | small variant ~2× faster, CPU-suitable | No |
| Chronos-Bolt | Apache-2.0 (?) | 9–205M | `chronos-forecasting` | No (external regressor only) | fast | No |
| TimesFM-2.5 | Apache-2.0 | 200M (+30M q-head) | `timesfm[torch]`, `timesfm[xreg]` (JAX) | Via XReg ridge (linear) | batch 8 on 8 GB RAM | No |
| TimesFM-3 | Non-commercial | 330M | `timesfm[torch]`, `google/timesfm-3.0-pytorch` | Native | ? | No |
| TiRex-2 | Apache-2.0 | 38.4M (+44.1M multivar) | `tirex-2` (also Darts) | Native | CPU OK; CUDA kernel needs VS Build Tools on Windows | No |
| TabPFN-TS | code Apache-2.0; TabPFN-3 weights non-commercial | 11M (v2 backbone); v3 ? | `tabpfn-time-series` | Known-future only (tabular) | slow locally (fev runtime ~280× Chronos-2) | Default cloud backend needs Prior Labs account |
| Moirai 2.0 | CC-BY-NC-4.0 | 11.4M (R-small) | `uni2ts` (from source) | Not documented | small | No |
| Toto 2.0 | Apache-2.0 | 4m–2.5B | `toto` / AutoGluon `Toto2Model` | No (planned) | 4m/22m small | No |
| TTM r2 | Apache-2.0 | ~1M+ | `granite-tsfm` | Only after fine-tuning | CPU/laptop | No |
| Sundial | Apache-2.0 | 128M | HF transformers | No (?) | ? | No |
| TimeGPT | proprietary | n/a | `nixtla` | Yes (`X_df`) | cloud | Yes |
| WindFM | ? | 8.1M | GitHub | ? | small | No |

### Inferences
- With ACF(24 h)≈0.1, only covariate-aware TSFMs are relevant: Chronos-2 (most practical: Apache-2.0, pip, AutoGluon/Darts wrappers, native F covariates), TiRex-2 (Apache-2.0, newest, but less-tested tooling), TimesFM-3 (non-commercial — acceptable for a hackathon only if organisers allow non-commercial weights; flag it), TimesFM-2.5+XReg (covariate effect is linear ridge — cannot learn the cubic/cut-in/cut-out power curve unless you feed engineered features such as ws³ or a fitted power curve), TabPFN-TS (theoretically best match to an "instantaneous NWP→power" mapping per Berthelier et al., but CPU-slow, non-commercial v3 weights and cloud-by-default).
- Chronos-2 with 8,192-step context sees ~341 days of hourly target+NWP pairs in-context; this is a genuine zero-shot "learn the power curve in context" mechanism, but the Berthelier result suggests it underfits instantaneous nonlinear mappings relative to tabular learners — so expect it to be a useful ensemble member rather than a GBM replacement.
- Fine-tuning TSFMs (the regime where the ERCOT study got ~3.8% nMAE) was done on A100s; on a CPU laptop in 4 h, fine-tuning a 120M model is risky; `chronos-2-small` (28M) fine-tune via AutoGluon is the only plausible CPU fine-tune candidate.
- GIFT-Eval rankings (univariate, now agent/ensemble-dominated) should be ignored for model choice here; fev-bench covariate subset and FETS are the relevant signals.

### Gaps
- No measured CPU (laptop) latency numbers for Chronos-2 / TiRex-2 / TimesFM-3 were found; fev-bench runtimes are normalized and likely GPU.
- fev-bench top-20 figures come from an aggregator mirror (tsfm.ai); the official leaderboard (HF Space) was not directly rendered. Identity/licence of "t0-beta", "TS-ICL", "citras-fm" not researched.
- Chronos-Bolt and WindFM exact licences not re-verified; TiRex v1 licence not verified.
- TabPFN-3 / 3.5 maximum context (rows) and whether 25k hourly rows fit locally on CPU: not verified.
- JAX (needed by `timesfm[xreg]`) Windows CPU wheel availability not verified — a potential Windows install risk.
- TimesFM-3 context length and CPU memory footprint not stated in the fetched pages.
- Moirai 2.0 covariate support: model card silent; uni2ts code may support `feat_dynamic_real` (Moirai 1.x did) — not verified.

---

## Q3. LLM-based forecasting (Time-LLM, LLMTime, GPT4TS, PromptCast): realistic value vs cost

### Takeaway
Ablations show the LLM component adds nothing: removing it or replacing it with a single attention layer matches or improves accuracy while cutting compute by up to ~1000×; for a CPU hackathon with a covariate-driven target, LLM-based forecasters are negative value.

### Cited Findings
- Tan et al. (NeurIPS 2024): on three popular LLM-based methods, removing the LLM or replacing it with a basic attention/transformer block did not degrade — often improved — accuracy; pretrained LLMs did no better than from-scratch models, did not capture sequential dependencies, did not help few-shot; simpler methods reduce train/inference time by up to three orders of magnitude — [arXiv 2406.16964](https://arxiv.org/abs/2406.16964), [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6ed5bf446f59e2c6646d23058c86424b-Abstract-Conference.html)
- neuralforecast's TimeLLM implementation supports no exogenous variables — [neuralforecast capabilities](https://nixtlaverse.nixtla.io/neuralforecast/docs/capabilities/overview.html)
- Method papers for reference: Time-LLM (reprogramming a frozen LLM) — [arXiv 2310.01728](https://arxiv.org/abs/2310.01728); LLMTime (zero-shot via digit tokenization with GPT-3/LLaMA) — [arXiv 2310.07820](https://arxiv.org/abs/2310.07820); GPT4TS / "One Fits All" (frozen GPT-2) — [arXiv 2302.11939](https://arxiv.org/abs/2302.11939); PromptCast (forecasting as text prompts) — [arXiv 2210.08964](https://arxiv.org/abs/2210.08964)
- GIFT-Eval added an "Agentic" model type; agentic/ensemble submissions now occupy the top of the leaderboard — [GIFT-Eval README](https://github.com/SalesforceAIResearch/gift-eval), [tsfm.ai GIFT-Eval mirror](https://tsfm.ai/benchmarks/gift-eval)

### Inferences
- Any LLM value in this project is at the **orchestration** level (writing code, feature ideas), not as the forecaster. LLM-based TS models need GPUs, have no future-covariate support in common implementations, and the evidence says they don't beat simple baselines.

### Gaps
- No wind-power-specific evaluation of LLM-based forecasters with NWP covariates was found.
- Agentic GIFT-Eval entries' internals (which base models/ensembles) were not investigated.

---

## Q4. Libraries: neuralforecast, Darts, GluonTS, PyTorch Forecasting, AutoGluon-TimeSeries, sktime, tsai — install weight, Windows, Python 3.12

### Takeaway
All major libraries support Python 3.12 in 2026 and run on Windows CPU; AutoGluon-TimeSeries (1.6.x) is the most "batteries-included" (GBM tabular models + DL + Chronos-2/Toto + ensembling, known covariates, quantiles), neuralforecast gives the cleanest F/H/S exog API for DL, and Darts uniquely wraps LightGBM/CatBoost/XGB plus Chronos-2/TimesFM/TiRex behind one covariate API; the main install cost is the PyTorch wheel (~200 MB CPU on Windows, with a reported ~590 MB dev-build bloat in 2025).

### Cited Findings
- AutoGluon: Python 3.10–3.13 on Linux/macOS/**Windows**; `pip install autogluon.timeseries`; CPU-only torch via `--extra-index-url https://download.pytorch.org/whl/cpu`; docs version 1.6.1 (dev 1.6.4) — [AutoGluon install](https://auto.gluon.ai/stable/install.html)
- AutoGluon-TimeSeries model zoo: baselines, statistical (ETS, AutoARIMA, Theta, NPTS…), DL (DeepAR, DLinear, PatchTST, SimpleFeedForward, TFT, TiDE, WaveNet), **tabular (DirectTabular, PerStepTabular, RecursiveTabular — support known/past covariates and static features)**, pretrained (Chronos2Model, ChronosModel incl. Bolt, TotoModel, Toto2Model) — [AutoGluon model zoo](https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-model-zoo.html)
- neuralforecast 3.2.2 (8 Sep 2026): Python ≥3.10, classifiers 3.10–3.13; Apache-2.0; deps PyTorch + Lightning; optional Ray/Optuna for Auto* tuning; conda-forge available — [PyPI neuralforecast](https://pypi.org/project/neuralforecast/)
- PyTorch Forecasting 1.8.0 (24 Jun 2026): Python ≥3.10,<3.15; MIT; TFT, N-BEATS, N-HiTS, DeepAR, LSTM/GRU/MLP; maintained under sktime (fkiraly, jdb78) — [PyPI pytorch-forecasting](https://pypi.org/project/pytorch-forecasting/)
- Darts: regression (LightGBM/CatBoost/XGB/linear) + torch models + foundation models (Chronos2Model, TimesFM2p5Model, TimesFM3Model, TiRexModel, PatchTSTFMModel); README indicates Python 3.11+ (not re-verified) — [Darts GitHub](https://github.com/unit8co/darts)
- PyTorch Windows CPU wheel: 207.0 MB (`torch-2.8.0.dev20250614+cpu-cp310-win_amd64`) jumped to 589.8 MB on the next nightly (PR #154783); final-release resolution not shown in the issue — [pytorch/pytorch#159515](https://github.com/pytorch/pytorch/issues/159515)
- Foundation-model packages: `chronos-forecasting` — [HF](https://huggingface.co/amazon/chronos-2); `timesfm[torch]`/`timesfm[xreg]` — [GitHub](https://github.com/google-research/timesfm); `tirex-2` — [GitHub](https://github.com/NX-AI/tirex-2); `tabpfn-time-series` — [PyPI](https://pypi.org/project/tabpfn-time-series/); `granite-tsfm` — [HF TTM](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2); `uni2ts` from source — [HF Moirai 2.0](https://huggingface.co/Salesforce/moirai-2.0-R-small); `nixtla` (TimeGPT API) — [PyPI](https://pypi.org/project/nixtla/)

### Inferences
- Fastest path on Windows CPU: one venv with `torch` (CPU) + `autogluon.timeseries` gives LightGBM/CatBoost tabular forecasters, TFT/TiDE/DeepAR, Chronos-2 zero-shot with known covariates, and a weighted ensemble, all in one API with quantile outputs. neuralforecast is the better choice if the team wants explicit control over TiDE/NHITS/TSMixerx with `futr_exog_list`.
- Pre-download HF weights (chronos-2 ≈ hundreds of MB; small variant less) before the hackathon; network/HF rate limits during the event are a real risk.
- Avoid TiRex-2 CUDA path and `timesfm[xreg]` (JAX) on Windows unless tested beforehand; TabPFN-TS default cloud backend requires an account and sends data off-machine.

### Gaps
- GluonTS, sktime and tsai current versions / Python 3.12–3.13 / Windows status were not verified in this session (GluonTS is used internally by AutoGluon's DL models per the model zoo list, but that was not explicitly confirmed on the page).
- Final PyTorch 2.8+/2.9+ Windows CPU wheel sizes not verified.
- Actual disk/RAM footprint of a full `autogluon.timeseries` install not found.

---

## Q5. Hybrid physics + ML, residual learning over a power curve, GBM + NN + FM ensembles, stacking

### Takeaway
The strongest day-ahead wind evidence favours physics-anchored models (power-curve prior + learned correction) and heterogeneous ensembles (GBDT + RNN in KDD Cup; TSFM + domain model in EPF; diverse ensembles in TabArena), and some TSFM tooling already implements residual schemes (TimesFM XReg, Chronos-Bolt covariate regressor).

### Cited Findings
- UniWind: Physical Prior Estimator (site-conditioned monotonic warping of a shared power curve) + Latent State Encoder (operational states: shutdowns, curtailment) + State-aware Power Corrector with bounded expert corrections; best across 24 farms in full-shot and 29–62% MAE better than FMs zero-shot — [arXiv 2607.01670](https://arxiv.org/html/2607.01670)
- Power-curve modelling beat autoregressive DL for day-ahead wind with weather forecasts and was cheaper/more robust to shutdown-contaminated history — [arXiv 2412.00423](https://arxiv.org/abs/2412.00423)
- KDD Cup 2022 88VIP: GBDT + RNN ensemble with timescale-specific sub-models — [arXiv 2208.08952](https://arxiv.org/abs/2208.08952)
- EPF: "simple ensembles of TSFMs and domain-specific methods appear to have significant potential" — [arXiv 2607.02623](https://arxiv.org/abs/2607.02623)
- TabArena: diverse ensemble outperformed all single models and AutoML systems; post-hoc ensembling is crucial — [arXiv 2506.16791](https://arxiv.org/abs/2506.16791)
- TimesFM-2.5 XReg modes = ridge regression on covariates + TimesFM on residuals (or reverse) — [TimesFM SKILL.md](https://github.com/google-research/timesfm/blob/master/timesfm-forecasting/SKILL.md), [Darts issue #2976](https://github.com/unit8co/darts/issues/2976)
- AutoGluon: Chronos-Bolt + CatBoost/LightGBM covariate regressor for per-timestep covariate effects; `chronos2_ensemble` preset mixes zero-shot and fine-tuned Chronos-2 — [AutoGluon Chronos tutorial](https://auto.gluon.ai/dev/tutorials/timeseries/forecasting-chronos.html)
- ERCOT study: adding weather inputs improved fine-tuned FMs (Moirai-L 4.17%→3.78% nMAE); unseen-site generalization cost 0.7–2.0 pp nMAE because wind is terrain-dependent — [arXiv 2604.22077](https://arxiv.org/html/2604.22077)

### Inferences
- A cheap, well-supported hybrid for this task: fit an empirical power curve P̂ = f(NWP wind speed at hub height) (binned/isotonic/logistic), then learn residual (or ratio) with GBM on NWP features; optionally stack a Chronos-2 (with the same NWP as known covariates) forecast as an extra feature or as a blend member with weights fit on a time-ordered validation split.
- Curtailment/shutdown periods in history must be masked or flagged, otherwise both the power curve and any sequence/ICL model (Chronos-2 context) learn corrupted relationships (consistent with Meisenbacher and UniWind's "operational state" component).

### Gaps
- No published quantitative comparison of "power-curve + GBM residual" vs "GBM on raw NWP" on hourly single-turbine data was found in this session.
- No study found that stacks Chronos-2/TiRex-2 with LightGBM specifically for wind power.

---

## Q6. Probabilistic outputs: quantile losses, distribution heads, conformal wrappers

### Takeaway
All relevant TSFMs natively emit quantiles (Chronos-2: 21, TimesFM: deciles via quantile head, Moirai 2.0: quantile loss), TFT/DL libraries support quantile/distribution losses, and conformal wrappers (neuralforecast `PredictionIntervals`, statsforecast `ConformalIntervals`, sktime `ConformalIntervals`) can calibrate any point model via time-series cross-validation.

### Cited Findings
- Chronos-2 outputs 21 quantiles (0.01–0.99); `predict_df(..., quantile_levels=[0.1,0.5,0.9])` — [Chronos-2 paper](https://arxiv.org/html/2510.15821), [HF](https://huggingface.co/amazon/chronos-2)
- TimesFM-2.5: optional 30M quantile head; deciles (0.1–0.9) plus median — [TimesFM GitHub](https://github.com/google-research/timesfm)
- Moirai 2.0 switched from distributional loss to quantile loss with multi-token prediction — [HF Moirai 2.0](https://huggingface.co/Salesforce/moirai-2.0-R-small)
- TFT is trained with quantile loss for prediction intervals — [arXiv 1912.09363](https://arxiv.org/abs/1912.09363)
- neuralforecast supports probabilistic forecasting and conformal intervals: `PredictionIntervals` calibrates intervals from cross-validation windows on point-loss models (same approach as MLForecast) — [neuralforecast conformal tutorial](https://nixtlaverse.nixtla.io/neuralforecast/docs/tutorials/conformal_prediction.html), [PyPI](https://pypi.org/project/neuralforecast/)
- sktime `ConformalIntervals` wrapper — [sktime docs](https://www.sktime.net/en/v0.20.0/api_reference/auto_generated/sktime.forecasting.conformal.ConformalIntervals.html); benchmarking of conformal TS methods — [arXiv 2601.18509](https://arxiv.org/pdf/2601.18509); temporal-dependence-aware conformal — [arXiv 2205.12940](https://arxiv.org/pdf/2205.12940); multi-step copula conformal — [arXiv 2212.03281](https://arxiv.org/pdf/2212.03281)
- WindFM targets both deterministic and probabilistic wind forecasting — [arXiv 2509.06311](https://arxiv.org/abs/2509.06311)

### Inferences
- If the hackathon metric is point-based (MAE/RMSE/nMAE), use the median (or mean for RMSE) from quantile models; if it is CRPS/pinball, quantile outputs from Chronos-2/AutoGluon or LightGBM quantile regression + split-conformal calibration on a time-ordered holdout are the lowest-effort options. Wind power is bounded [0, P_rated], so clip quantiles and prefer per-hour-ahead or per-power-bin calibration (errors are heteroscedastic: largest on the steep part of the power curve).

### Gaps
- No verified evidence comparing conformal-calibrated GBM intervals vs native TSFM quantiles on wind power.
- Exact neuralforecast loss class names (MQLoss, DistributionLoss) were not re-verified in this session.
