# Analogous solutions: competition winners, open-source repos, production systems, agentic demos, and README/reproducibility best practices for NWP-based wind power forecasting

Scope note: this catalogue covers reference implementations and lessons learned only. It is not a solution design. Research date: 2026-09-23. Star counts and licences are as reported by the fetched pages on that date. "Not verified" means the page did not show it.

---

## Q1. Competition winners and write-ups (GEFCom2012/2014, KDD Cup 2022 SDWPF, HEFTCom2024, Kaggle/ENS/EDP challenges)

### Takeaway
In every NWP-driven wind competition from GEFCom2012 to HEFTCom2024, the winners used gradient-boosted trees (GBM, LightGBM or CatBoost) on engineered NWP features: leads and lags of the forecast, smoothed wind, one model per NWP source, then stacking. The margins came from feature engineering, data cleaning, validation and post-processing for outages, not from exotic architectures. KDD Cup 2022 (SCADA-only, no NWP) is the exception: there, deep sequence models were competitive, but the top 10 were within about 0.9% of each other.

### Cited Findings

**GEFCom2012 wind track (Kaggle)**
- Task: hourly power for 7 wind farms, up to 48 h ahead. Team Leustagos (Lucas Silva) won both the public and private leaderboards. Method: time and weather features, then gradient-boosted decision trees plus linear regression. Paper: "A feature engineering approach to wind power forecasting: GEFCom 2012", IJF 30(2):395–401 — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0169207013000836); [EconPapers](https://econpapers.repec.org/article/eeeintfor/v_3a30_3ay_3a2014_3ai_3a2_3ap_3a395-401.htm)
- Winner's code and write-up (.odt) on GitHub: [lucaseustaquio/gefcom-2012-wind-track](https://github.com/lucaseustaquio/gefcom-2012-wind-track/blob/master/doc/GEFCom2012-Wind-Leustagos.odt). Competition page: [Kaggle GEF2012-wind-forecasting](https://www.kaggle.com/competitions/GEF2012-wind-forecasting). Paper index: [Hong's blog, GEFCom2012 papers](http://blog.drhongtao.com/2014/03/gefcom2012-papers.html)
- A later open repo reuses GEFCom2012 data with a combined LSTM + LightGBM framework for deterministic and probabilistic forecasts: [superkailang/WPP2012](https://github.com/superkailang/WPP2012)

**GEFCom2014 wind track (probabilistic)**
- GEFCom2014 had 4 tracks (load, price, wind, solar) and 581 participants from 61 countries. Wind data: 10 farms, 2012–2013, with NWP wind speeds (u/v) hourly at 10 m and 100 m. The target was a full predictive distribution scored by quantile (pinball) loss. Overview: Hong, Pinson et al. 2016, "Probabilistic energy forecasting: GEFCom2014 and beyond" — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0169207016000133); [Hong blog](http://blog.drhongtao.com/2016/01/probabilistic-energy-forecasting-gefcom2014.html); [Wikipedia](https://en.wikipedia.org/wiki/Global_Energy_Forecasting_Competition)
- Most winning wind teams used off-the-shelf ML or statistical methods (multiple quantile regression) with heavy manual feature selection — [Semantic Scholar summary of Hong & Pinson 2016](https://www.semanticscholar.org/paper/Probabilistic-energy-forecasting:-Global-Energy-and-Hong-Pinson/93df6c31cd5ee348f1986fda3a79d3c93dde0087)
- Winner kPower was 1st overall and 1st in 11 of 12 tasks. It fitted quantile-loss GBMs independently per zone and per quantile. Its strongest features were bidirectional lagged 100 m wind forecasts (t−k and t+k of the NWP series). It also smoothed the dominant NWP signal to absorb timing errors, used a cross-sectional approach, and added a two-layer model that exploits correlated neighbouring farms — ["Probabilistic gradient boosting machines for GEFCom2014 wind forecasting", IJF](https://www.sciencedirect.com/science/article/abs/pii/S0169207016000145); [ResearchGate](https://www.researchgate.net/publication/299459109_Probabilistic_gradient_boosting_machines_for_GEFCom2014_wind_forecasting)
- Another GEFCom2014 approach used multiple quantile regression across the wind, solar and price tracks — [ResearchGate](https://www.researchgate.net/publication/301773887_A_multiple_quantile_regression_approach_to_the_wind_solar_and_price_tracks_of_GEFCom2014). On the solar track, GBM combined with kNN was used — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0169207015001375)

**KDD Cup 2022, Baidu Spatial Dynamic Wind Power Forecasting (SDWPF)**
- Data: 134 turbines at 10-min resolution. The Scientific Data release covers Jan 2020–Dec 2021 with more than 11.4 M records. The score combines MAE and RMSE. More than 2,400 teams registered. 1st place HIK scored 44.917, 10th place 45.327, and the GRU baseline 47.850: 6.13% separates the winner from the baseline and only 0.906% separates 1st from 10th — [SDWPF paper (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11187227/); [arXiv 2208.04360](https://arxiv.org/abs/2208.04360)
- Official GRU baseline code: [PaddlePaddle/PaddleSpatial wpf_baseline_gru](https://github.com/PaddlePaddle/PaddleSpatial/tree/main/apps/wpf_baseline_gru). Competition page: [aistudio.baidu.com/competition/detail/152](https://aistudio.baidu.com/competition/detail/152/0/introduction). Workshop papers: [baidukddcup2022.github.io](https://baidukddcup2022.github.io/papers/Baidu_KDD_Cup_2022_Workshop_paper_0328.pdf)
- 3rd place of 2,490: a single Transformer/BERT model built with the author's `tfts` library — [LongxingTan/KDDCup2022-WPF](https://github.com/LongxingTan/KDDCup2022-WPF); paper [arXiv 2307.09248 (Teletraan, BERT)](https://arxiv.org/pdf/2307.09248)
- 6th place ("didadida_hualahuala", score −45.18): an ensemble of MDLinear and XGTN — [shaido987/KDD_wind_power_forecast](https://github.com/shaido987/KDD_wind_power_forecast)
- Team 88VIP technical report: [arXiv 2208.08952](https://arxiv.org/pdf/2208.08952). General mirror/notes repo: [ZongXR/Baidu_KDD_CUP_2022](https://github.com/ZongXR/Baidu_KDD_CUP_2022)

**HEFTCom2024 (IEEE Hybrid Energy Forecasting and Trading Competition): the most relevant modern analog, because it involved daily live submissions driven by NWP**
- Setup: a 3-month live competition (Feb 19–May 19, 2024) on Hornsea 1 wind (1.2 GW) plus East England solar (2.4 GW). Inputs were DWD ICON-EU and NCEP GFS, 4 runs per day. Targets were 9 quantiles (q10…q90) per half-hour, scored with pinball loss, with a daily 09:20 UTC deadline. 170 teams registered, 66 submitted, 24 completed, and 37 wrote methodology reports. Organised by Jethro Browell (Glasgow) and the IEEE PES WG on Energy Forecasting, sponsored by Ørsted — [HEFTCom2024 paper, arXiv 2507.01579](https://arxiv.org/html/2507.01579v1); [rebase.energy challenge page](https://www.rebase.energy/challenges/heftcom2024)
- Forecasting ranking (pinball, MWh): 1 SVK 22.18 (CatBoost), 2 UI BUD 23.18 (GBM), 3 Rnt 24.64 (NN on AI-weather embeddings), 4 GEB 25.16 (trees), 5 BridgeForCast 25.34 (GBM). Trading ranking: SVK £88.88 m, Rnt £88.29 m, GEB £88.18 m — [arXiv 2507.01579](https://arxiv.org/html/2507.01579v1)
- SVK (winner): separate CatBoost MultiQuantile models per NWP source (DWD, GFS and MET Norway MEPS), fitted separately for wind and solar. Features were raw, lagged and differenced NWP grid points plus calendar features. Only the number of boosting iterations was tuned; everything else stayed at defaults. A meta-model of linear quantile regression per target quantile took all 27 predicted quantiles as input. SVK also clipped quantiles using REMIT outage notices, after a cable fault cut Hornsea capacity — [arXiv 2507.01579](https://arxiv.org/html/2507.01579v1)
- Adding a third NWP source (MEPS) to GFS and DWD improved the pinball score by about 8% for SVK. But UI BUD and GEB placed top 5 without any external weather data, so implementation mattered as much as data — [arXiv 2507.01579](https://arxiv.org/html/2507.01579v1)
- Organiser lessons:
  - GBDTs remain dominant for day-ahead wind and solar; "forecaster expertise, data quality, preprocessing strategies, and validation techniques" were decisive.
  - 75% of the top 5 forecast wind and solar separately and then combined them.
  - Features were chosen through train/validation experiments, not EDA alone; default hyperparameters were often kept.
  - Teams that forecast total output directly struggled to adapt to the capacity-loss event. Teams with a separate wind model could simply post-process it.
  - Forecast skill converts to money: about −£0.18 m revenue per MWh of pinball, p < 0.001.
  - Source: [arXiv 2507.01579](https://arxiv.org/html/2507.01579v1)
- Winner paper: Olauson, Viotti, Huss, "The HEFTCom2024 winning model: a stacked CatBoost approach for probabilistic wind and solar power forecasting", IJF (2026) — [IDEAS/RePEc IJF listing](https://ideas.repec.org/s/eee/intfor.html). No public code repo for SVK was found.
- Team GEB (3rd trading, 4th forecasting, 1st student team) stacked "sister" forecasts built from different NWPs. It also used online solar post-processing for distribution shift, probabilistic aggregation of quantiles and a stochastic trading strategy — [arXiv 2505.10367](https://arxiv.org/abs/2505.10367); [IJF](https://www.sciencedirect.com/science/article/abs/pii/S0169207025001104). The code is MIT-licensed, 32 stars, LightGBM, with folders `/data /models /train /test /pre-process`, a conda env file, `requirements.txt` and scripts mapped to paper results — [BigdogManLuo/HEFTcom24](https://github.com/BigdogManLuo/HEFTcom24)
- Organiser quick-start repo (48 stars): API wrappers, a "Getting Started.ipynb" notebook, and `auto_submitter.py` (download new data → run model → submit, scheduled daily with Windows Task Scheduler before 09:20 UTC). The API key lives in a git-ignored `team_key.txt`. Licence not shown — [jbrowell/HEFTcom24](https://github.com/jbrowell/HEFTcom24). Analysis reproduction: [jbrowell/HEFTcom24-Analysis](https://github.com/jbrowell/HEFTcom24-Analysis). Full data including all submissions: Zenodo DOI 10.5281/zenodo.13950764 — [arXiv 2507.01579](https://arxiv.org/html/2507.01579v1)

**Other challenges**
- ENS Challenge Data × CNR (Compagnie Nationale du Rhône): day-ahead hourly production for 6 wind farms from multiple NWP models. Example solution repo (36 stars, Colab notebook, licence not shown): [qcha41/wind-power-forecasting-challenge](https://github.com/qcha41/wind-power-forecasting-challenge)
- Kaggle "ML&E 20/21 Wind Power Forecasting Competition" (class competition): [kaggle.com/c/mle2021](https://www.kaggle.com/c/mle2021). ASHRAE Great Energy Predictor III overview (energy, not wind): [arXiv 2007.06933](https://arxiv.org/pdf/2007.06933). Kaggle forecasting lessons paper: [arXiv 2009.07701](https://arxiv.org/pdf/2009.07701)
- EDP "Hack the Wind" (48 h hackathon) was predictive maintenance on 2 years of SCADA from 5 turbines plus a met mast, predicting failures up to 60 days ahead and valued by savings. Winners (Ginkgo Analytics, Boldare) delivered web apps with integrated AI and ROI framing versus reactive maintenance — [EDP Hack the Wind](https://edp.com/en/innovation/data/reuses/hack-wind); [EDP OpenData 2018](https://opendata.edp.com/pages/hackthewind/); [Boldare case study](https://www.boldare.com/work/case-study-predictive-maintenance/); [LinkedIn write-up](https://www.linkedin.com/pulse/predicting-failures-wind-turbines-ren%C3%A9-hommel-dr-)

### Inferences
- The benchmark recipe repeated across 12 years of competitions:
  1. Per-horizon or global GBDT on NWP wind at hub height (100 m), with speed, u/v and direction.
  2. NWP leads and lags (t±1…±3 h) and rolling smoothing of the NWP wind.
  3. Calendar and hour features.
  4. One model per NWP source (ECMWF/GFS/ICON), then a simple stack or linear quantile regression.
  5. Quantile outputs (P10/P50/P90), sorted to avoid crossing.
  6. Post-processing for known capacity changes or outages.
- For a hackathon with 2 turbines and 1 month of replay, the HEFTCom operational pattern maps most closely: a daily scheduled job pulls the NWP issued that day, runs the model, writes the submission and logs it. The organisers' `auto_submitter.py` is a small, citable precedent.
- KDD Cup 2022 shows the limits of SCADA-only deep models: small gains over a GRU baseline, and 1st to 10th within 1%. It supports keeping baselines (persistence, raw power curve) in any results table.
- EDP Hack the Wind winners' focus on a usable app plus ROI echoes the "value" judging criterion.

### Gaps
- No public code repo found for the HEFTCom2024 winner (SVK / Olauson et al.). The IJF paper was not fetched.
- KDD Cup 2022: 1st (HIK) and 2nd place methods and repos not verified. Only 3rd and 6th have confirmed repos.
- Chinese State Grid / China renewable forecasting competitions (e.g., State Grid "新能源功率预测" contests) were not researched. No sources collected.
- DrivenData energy challenges and a Kaggle "Wind Power Generation Forecasting" dataset competition were not specifically located.
- GEFCom2014 kPower author names and exact feature list: only the abstract-level summary was retrieved.

---

## Q2. Open-source GitHub projects (NWP-based wind forecasting, OCF, windpowerlib, OpenOA, Open-Meteo-based, forecasting libraries)

### Takeaway
No mature open-source "NWP → wind power" product exists for arbitrary sites. The closest analogs are:
- **Open Climate Fix (OCF):** a production-grade Open-Meteo NWP → GBM approach for solar (MIT); its WindNet-India model is on Hugging Face.
- **Wind power-curve libraries:** windpowerlib and OpenOA.
- **Small 2025–2026 personal and hackathon repos:** these combine Open-Meteo archived forecasts, a physics power curve, a LightGBM residual model and quantile/conformal bands.

### Cited Findings

**Open Climate Fix (OCF)**
- **open-source-quartz-solar-forecast** (MIT, 156 stars, 113 forks, 36 contributors, 526 commits): 0–48 h site-level PV forecast from Open-Meteo NWP (GFS, ICON, ECMWF IFS). The default GBM was trained on 25k UK sites; an XGBoost alternative uses 14 Open-Meteo features. It ships a FastAPI API, Docker, a React/Streamlit UI, notebooks/Colab and `python scripts/run_evaluation.py` with a committed test set (`dataset/testset.csv`, 50 sites). MAE is 0.1906 kW, about 13% of capacity excluding night. The README flows: quick start → Colab → generating forecasts → install → model description → evaluation results → known restrictions → dev setup → abbreviations. Forecasts older than 90 days fall back to historical weather — [GitHub](https://github.com/openclimatefix/open-source-quartz-solar-forecast)
- **windnet_india** (Hugging Face): OCF's WindNet uses NWP (e.g., ECMWF) to forecast wind in NW India 48 h ahead at 15-min granularity. Trained 2019–2022, validated 2022–2023 — [HF model card](https://huggingface.co/openclimatefix/windnet_india)
- **india-forecast-app**: runs the wind and PV forecasts for India and saves them to a database (operational app pattern) — [GitHub](https://github.com/openclimatefix/india-forecast-app). OCF's commercial wind work serves Rajasthan's grid operator with day-ahead and intraday wind — [OCF wind page](https://www.openclimatefix.org/work/wind-forecasting)
- **PVNet** (OCF's main deep PV model repo): [openclimatefix/PVNet](https://github.com/openclimatefix/PVNet). Org overview: [github.com/openclimatefix](https://github.com/openclimatefix)

**Wind physics and analytics libraries**
- **windpowerlib**: models turbine and farm output. It ships turbine data (power curves, hub heights) via the OpenEnergy Database, and models farm wake losses through a farm-efficiency curve or reduced wind speeds. Tested on Python ≥ 3.10 — [wind-python/windpowerlib](https://github.com/wind-python/windpowerlib); [releases](https://github.com/wind-python/windpowerlib/releases). Licence not verified on page.
- **OpenOA** (NREL): operational assessment of wind plants. Its `PlantData` schema combines SCADA, met towers, revenue meters and reanalysis (ERA5/MERRA-2), and a power-curve module fits curves to SCADA — [NREL/OpenOA](https://github.com/NREL/OpenOA). Flag: the repo now appears under the org `NatLabRockies` ([NatLabRockies/OpenOA v3.1.2](https://github.com/NatLabRockies/OpenOA/tree/v3.1.2)), so the old NREL URL likely redirects.
- Unified turbine power and thrust curve database: [Divi-patel/wind-power-curves](https://github.com/Divi-patel/wind-power-curves)

**Open-Meteo archived-forecast data (directly relevant to "forecast as of issue date")**
- **Previous Runs API** (`https://previous-runs-api.open-meteo.com/v1/forecast`): variables take the suffix `_previous_dayN`, N = 0…7. `_previous_day1` is the value predicted 24 h earlier, `_previous_day2` 48 h earlier. Archive depth: from Jan 2024 for most models, GFS 2 m temperature from Mar 2021, JMA from 2018. Covers ECMWF IFS, GFS, ICON, ARPEGE/AROME, JMA, KMA, GEM, BOM, CMA, UKMO, MeteoSwiss, MET Norway and others. Wind speed and direction at 80/100/120/180/200 m. It gives fixed lead-time offsets, not whole runs; for a full single run (init time plus all hours) use the **Single Runs API** with `&run=` — [Previous Runs docs](https://open-meteo.com/en/docs/previous-runs-api); [Single Runs API](https://open-meteo.com/en/docs/single-runs-api); [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api); [Open-Meteo blog on previous runs](https://openmeteo.substack.com/p/weather-forecasts-from-previous-model-runs)
- Community discussion on bias correction with Open-Meteo historical forecasts: [open-meteo discussion #1023](https://github.com/open-meteo/open-meteo/discussions/1023). Server code is AGPLv3; AWS open data: [open-meteo/open-data](https://github.com/open-meteo/open-data)

**Small, recent reference repos (good pattern sources, low stars, mostly no licence)**
- **Kr1sh-Parmar/hackout-26 ("ZERO BIAS")**, 0 stars, licence not stated, 2026 hackathon repo:
  - Pipeline: Weather → physics model (pvlib; IEC 61400 wind power curve) → LightGBM on capacity-factor residuals → quantile regression P10/P50/P90 → split-conformal calibration.
  - Models are organised as a "ladder of rungs" from persistence up to GNNs; deep models were benchmarked but not served.
  - Data: Open-Meteo Historical API plus Previous Runs (lead-time bands 24–95 h), Elia generation data, and a medallion `raw/bronze/silver/gold` layout.
  - Reported wind nRMSE 8.57%, skill 0.69, PICP 0.79. 211 tests.
  - Quickstart: `pip install -e ".[dev]"` → `pytest` → `scripts/backtest.py` → `scripts/run_cycle.py` → `uvicorn` API. Data sources listed in `SOURCES.md`.
  - [GitHub](https://github.com/Kr1sh-Parmar/hackout-26)
- **RyanBantu/bjorko-wind-power-forecast**, 0 stars, no licence: 15-min day-ahead forecast for a 45 kW research turbine. Empirical monotonic PCHIP power curve (0.5 m/s bins, auto cut-in) and linear MOS on NWP wind cut wind-speed bias from −0.957 to +0.009 m/s out-of-sample. Leave-one-day-out CV over 44 days. Power nRMSE 0.274. NWP comes from SMHI live and Open-Meteo Historical Forecast API for backtests. The README includes a results table, limitations and dataset citation — [GitHub](https://github.com/RyanBantu/bjorko-wind-power-forecast)
- **lucianocnsl/Wind-power-forecast**: notebook estimating output of an 80 m rotor, 1,670 kW turbine from Open-Meteo hourly wind and temperature — [GitHub](https://github.com/lucianocnsl/Wind-power-forecast)
- **siddhantmishra-4098/weather-energy-analytics**: end-to-end ECMWF open-data IFS GRIB2 ingest (cfgrib/ecCodes/xarray) → dashboard, forecast-bias analysis and a Bayesian weather-to-generation model (Germany) — [GitHub](https://github.com/siddhantmishra-4098/weather-energy-analytics)
- GitHub topic index: [topics/wind-power-forecasting](https://github.com/topics/wind-power-forecasting); [topics/wind-energy](https://github.com/topics/wind-energy)

**Forecasting libraries with exogenous (NWP) covariates**
- Nixtla statsforecast and neuralforecast support exogenous regressors such as weather — [statsforecast](https://github.com/Nixtla/statsforecast); [neuralforecast](https://github.com/nixtla/neuralforecast); [Nixtla exogenous docs](https://nixtlaverse.nixtla.io/neuralforecast/docs/capabilities/exogenous_variables.html). Darts wraps statsforecast models — [Hyndman overview of Python TS libs](https://robjhyndman.com/hyndsight/python_time_series.html)

### Inferences
- Reusable parts for a 2-turbine, Open-Meteo-based project:
  - windpowerlib or an OEDB power curve as the physics baseline, or an empirical PCHIP curve fitted from SCADA (bjorko pattern).
  - The Open-Meteo Previous Runs `_previous_day1` / `_previous_day2` suffixes (or Single Runs with `&run=`) to guarantee "as-of-issue-date" inputs without look-ahead.
  - The OCF quartz README and evaluation-script layout as a model for documentation.
  - hackout-26's "physics → GBM residual → quantiles → conformal" ladder and its committed test suite as a hackathon-grade pattern.
- The Historical Forecast API is not interchangeable with Previous Runs for issue-date replay. Based on the docs' framing, it stitches together recent runs, so using it for a 24–48 h backtest risks optimistic (leaky) skill. Verify on Open-Meteo docs before relying on this.
- Previous Runs archive depth (from Jan 2024) means Feb 2026 replay is covered, and roughly two years of training data are available for most models.

### Gaps
- Star counts and licences for windpowerlib, OpenOA, PVNet and india-forecast-app were not fetched.
- Archive status was not systematically checked. KDD 2022 repos are likely inactive but not flagged as archived on the pages seen.
- Elia and Energinet open forecasting models were not researched. skforecast and Darts wind-specific examples were not located. No dedicated "SDWPF + NWP" open repo was found.

---

## Q3. Commercial and production systems (architecture inspiration, typical pipeline, quoted accuracy)

### Takeaway
Production wind forecasting systems share one pattern: ingest several NWPs, apply site-specific post-processing (MOS or ML on SCADA), combine weather models weighted by situation, update intraday from live measurements, attach an uncertainty band, and handle availability and curtailment explicitly. Vendors publish mostly relative improvements rather than absolute NRMSE.

### Cited Findings
- **WPPT (DTU/ENFOR)**: online tool, originally up to 36 h ahead, in operation at the Eltra/Elsam dispatch centre since Oct 1997. It uses online NWP plus online measurements to update models continuously. The core is a semi-parametric wind-farm power curve in wind speed and direction, plus dynamic models for power dynamics and diurnal variation. Models are self-calibrating and adapt to changes in turbine count, the environment, NWP model changes, roughness and dirty blades — [DTU Orbit](https://orbit.dtu.dk/en/publications/wppt-a-tool-for-on-line-wind-power-prediction); [OSTI report](https://www.osti.gov/etdeweb/biblio/20599421); [ENFOR offshore paper](https://enfor.dk/pub/bib/paprep/public/CPHoffshore05.pdf); [IntechOpen chapter](https://www.intechopen.com/chapters/81755)
- **Prediktor (Risø)**, a competing system, uses Model Output Statistics fed by historical farm data to correct NWP bias and scaling — [IntechOpen chapter](https://www.intechopen.com/chapters/81755); [Landberg et al. 2003 review, Wind Energy](http://henrikmadsen.org/wp-content/uploads/2016/02/Landberg_et_al-2003-Wind_Energy.pdf)
- **energy & meteo systems, previento** (all from [emsys wind power forecasts](https://www.emsys-renewables.com/products/power_forecasts/wind-power-forecasts.php)):
  - Uses NWP from "all leading weather services", combined with the "KombiBox" method, which gives more weight to the models with the lowest error for the current weather situation.
  - Physically models local site conditions and known shutdowns (night, storm, bat curtailment).
  - Horizon from 5 min to 15 days, with uncertainty computed per forecast situation.
  - Two products: a **real feed-in** forecast (includes grid curtailment and maintenance) and a **technical feed-in** forecast (excludes market/grid curtailment).
  - Covers more than 400 GW of wind.
- **Meteomatics**: the EURO1k 1-km pan-European model (48 h horizon) reduced wind-power nRMSE by up to 8.1% intraday and 8.5% day-ahead — [EGU 2024 abstract (ADS)](https://ui.adsabs.harvard.edu/abs/2024EGUGA..2617204T/abstract). Marketing claims "up to 50%" wind improvement with ML, and one customer with 500+ plants (1,100+ MW) — [Meteomatics news](https://www.meteomatics.com/en/news/ai-for-solar-and-wind-power-forecasts/); [Meteomatics wind power](https://www.meteomatics.com/en/energy-forecasting/wind-power/). The "50%" figure is vendor marketing with an undefined baseline.
- **Open Climate Fix "Quartz Wind"**: day-ahead and intraday wind forecasts for the Rajasthan grid operator. It combines NWP, satellite and topography with ML — [OCF](https://www.openclimatefix.org/work/wind-forecasting)
- **Ørsted** sponsored HEFTCom2024, and the competition's operational realism (live daily NWP, outages, missing data) was framed as the thing academic benchmarks lack — [arXiv 2507.01579](https://arxiv.org/html/2507.01579v1)
- International best-practice brief on VRE forecasting (GET.transform, Jan 2024; PDF could not be text-extracted in this session) — [GET.transform brief](https://www.get-transform.eu/wp-content/uploads/2024/01/GET.transform-Brief_VRE-Forecasting-Solar-Wind.pdf)

### Inferences
- A defensible "production-like" architecture for the hackathon narrative:
  1. NWP ingest per issue time (multi-model if available).
  2. Physics power curve plus a statistical or ML correction layer (MOS).
  3. Model combination (a KombiBox-like weighting, or HEFTCom-style stacking).
  4. Probabilistic band.
  5. An availability/curtailment flag (real vs technical forecast).
  6. Monitoring of error versus actuals, with adaptive recalibration (WPPT-style).

  An agent can reasonably own steps 4–6 as QA and monitoring, rather than generating numbers.
- Distinguishing a "technical" forecast (turbine can produce) from a "real feed-in" forecast (after curtailment) is an industry convention worth mirroring when actuals contain curtailment or downtime.

### Gaps
- No quoted absolute accuracy (NRMSE/NMAE) was retrieved for single-turbine or single-farm day-ahead from vendors. The GET.transform PDF was unreadable via fetch. Typical literature ranges were not sourced in this session.
- Vortex, Solargis (mainly solar), enercast, Greenbyte/Power Factors, Nnergix, Vattenfall/Ørsted in-house systems and Chinese vendors (e.g., Goldwind, Envision, State Grid EPRI) were not researched. No citable material was collected.

---

## Q4. Agentic / LLM demos in wind and energy forecasting (GitHub)

### Takeaway
The credible pattern in 2025–2026 repos keeps forecasting in a classical ML model (GBM) and uses a LangGraph-style agent for four jobs: orchestration (ingest → forecast → diagnose), conditional routing (e.g., a retrain recommendation when error drifts), RAG over domain documents, and natural-language reports. The LLM does not produce the numeric forecast. LLM-as-forecaster exists in research code, but for ultra-short-term horizons.

### Cited Findings
- **fborbon/windward** (0 stars, last commit 2026-09-18, licence not stated, live demo at windward.forwardforecasting.eu) — [GitHub](https://github.com/fborbon/windward):
  - **Agent:** a LangGraph state machine in `agents/graph.py` with nodes ingest → forecast (loads the registered MLflow model) → diagnose (power curve, Cp/Betz efficiency, anomalies) → parallel rag + multimodal (vision-LLM blade check) → investigate (forecast-error trend plus model age) → conditional recommend / recommend_retrain → explain (natural-language report).
  - **Forecast model:** sklearn GradientBoostingRegressor (200 trees, depth 4) with 8 features: wind speed, speed³, direction, temperature, pressure, air density, price and hour. Trained on open SCADA (Kelmarsh, Penmanshiel, Hill of Towie; CC BY 4.0) joined with Open-Meteo. Kelmarsh test MAE 1.06 MW, R² 0.73.
  - **Stack:** LangGraph, LangChain, LlamaIndex, FAISS, Bedrock, LiteLLM, Langfuse tracing, MLflow, FastAPI, MCP server, Docker.
  - **README:** skill-to-component table, architecture flowchart, agent workflow diagram, data-source registry, results table, project tree, setup, roadmap, and cost breakdown.
- **Anuri-ops/langgraph-energy-agent**: a LangGraph agent orchestrating its own RAG (documents) and NL-to-SQL (data) tools for energy Q&A — [GitHub](https://github.com/Anuri-ops/langgraph-energy-agent)
- **GRA-LLM**: a gated retrieval-augmented LLM for ultra-short-term wind power forecasting. It combines FAISS retrieval of similar historical windows, a dynamic trust gate and physical cut-in wind-speed constraints — [GitHub](https://github.com/jianghu511321/GRA-LLM-Gated-Retrieval-Augmented-LLM-for-Wind-Power-Forecasting)
- Curated list of energy + LLM papers: [chenweilong915/awesome_energy_LLM](https://github.com/chenweilong915/awesome_energy_LLM). Research: "Can Large Language Model Agents Balance Energy Systems?" [arXiv 2502.10557](https://arxiv.org/pdf/2502.10557); review "LLM Agent Based Renewable Energy Forecasting Using Edge and IoT Data" [arXiv 2605.25141](https://arxiv.org/pdf/2605.25141); agentic digital twins review [arXiv 2506.06359](https://arxiv.org/pdf/2506.06359)
- The hackathon repo hackout-26 explicitly has no LLM/agent: decisions flow from ML plus an LP optimiser — [GitHub](https://github.com/Kr1sh-Parmar/hackout-26). This contrasts with "agentic" framing requirements.

### Inferences
- For an "Agentic AI" judging criterion, windward is the closest reference. It shows what reviewers can see: named graph nodes, conditional edges driven by measurable triggers (error trend, model age), tool calls, traces (Langfuse) and a generated report.
- A deterministic fallback (running without an LLM key) is not shown in windward, but it matters for reproducibility-gated judging. This is an inference, not a sourced practice.

### Gaps
- No CrewAI-based wind forecasting repo was found. No agentic demo using Open-Meteo archived forecast replay (issue-date backtest) was found.
- No quantitative evidence was found that agent layers improve forecast accuracy. Existing demos justify agents by orchestration and explainability.

---

## Q5. Reproducibility and README best practices that maximise hackathon (and AI-judge) scores

### Takeaway
Reviewers, human or AI, reward repos that satisfy three conditions:
1. **It runs:** one command from a fresh clone, pinned deps, committed sample data and outputs.
2. **It proves claims:** a results table produced by an eval command, with baselines.
3. **It explains:** architecture diagram, limitations, where AI is used and why.

AI judge tools already exist that execute README commands in a clean sandbox and score repos against a rubric.

### Cited Findings
- **Papers with Code ML Code Completeness Checklist** (NeurIPS recommendation) has 5 items:
  1. Dependency specification.
  2. Training code.
  3. Evaluation code.
  4. Pre-trained models.
  5. A README with a results table and the exact commands that produce those results.

  NeurIPS 2019 repos with all 5 had the most stars (median 196, mean 2,664). A README template sits in `templates/` — [paperswithcode/releasing-research-code](https://github.com/paperswithcode/releasing-research-code); [README](https://github.com/paperswithcode/releasing-research-code/blob/master/README.md); [templates](https://github.com/paperswithcode/releasing-research-code/tree/master/templates); [Medium: ML Code Completeness Checklist](https://medium.com/paperswithcode/ml-code-completeness-checklist-e9127b168501)
- **Cookiecutter Data Science v2** structure: `LICENSE, Makefile, README.md, data/{external,interim,processed,raw}, docs/, models/, notebooks/` plus a source package. Its opinions are that raw data is immutable (never edit in place) and that you should flatten structure when a project is small — [CCDS docs](https://cookiecutter-data-science.drivendata.org/); [Opinions](https://cookiecutter-data-science.drivendata.org/opinions/); [CCDS v2 blog](https://drivendata.co/blog/ccds-v2); [GitHub](https://github.com/drivendataorg/cookiecutter-data-science)
- **Made With ML** (30K+ stars): MLOps course with lessons on scripting, reproducibility, packaging, pre-commit, logging, versioning and testing — [madewithml.com](https://madewithml.com/); [GokuMohandas/Made-With-ML](https://github.com/GokuMohandas/Made-With-ML); [mlops-course](https://github.com/GokuMohandas/mlops-course)
- **A hackathon judge's lessons** — [DEV: What I learned reviewing AI projects as a hackathon judge](https://dev.to/amising6/what-i-learned-after-reviewing-many-ai-and-developer-projects-as-a-hackathon-judge-2g06):
  - State the problem, the prior state, what improved, the technical choices, and what the user can do now.
  - A clear README, architecture diagram, demo video, screenshots, setup steps and documented limitations significantly strengthen evaluations.
  - Explain realistic AI use; don't claim AI "magically built" it.
  - Show production thinking: error handling, observability, security, privacy.
  - A focused working demo beats a bigger unproven idea.
- Build the reproducible environment (container, lockfile, one-command setup) first, not last. State limitations honestly, since that "reads as judgment". One command should go from a fresh clone to every claim (build, test, fetch, benchmark, regenerate docs) — [DEV: how an AI hackathon will be judged](https://dev.to/marvinoka4/5900-engineers-just-registered-for-a-hackathon-where-using-ai-is-the-point-heres-how-it-will-1bdd); [SANKHYA issue #73, one-command reproducibility](https://github.com/thegoodengineers/SANKHYA/issues/73)
- **AI judge tooling that exists (2026):**
  - [Daku3011/AI-Hackathon-Judge](https://github.com/Daku3011/AI-Hackathon-Judge) scores a repo, deck and demo video with 5 AI personas (VC, CTO, Product, UI/UX, Professor) and aggregates the votes.
  - [Nathanjr123/repo-testify](https://github.com/Nathanjr123/repo-testify) "executes a repository's own README claims in a clean sandbox" and returns an evidence-linked verdict per claim.
  - [Jazztinn/dontreadme](https://github.com/Jazztinn/dontreadme) writes a judge-ready README grounded in real repo paths and commands, mapped to the rubric.
  - [ETHGlobal AIJudge](https://ethglobal.com/showcase/aijudge-oeihx) analyses the description, code and video against custom rubrics.
- Devpost guidance on submission and judging criteria: [Devpost blog](https://info.devpost.com/blog/understanding-hackathon-submission-and-judging-criteria)
- **Exemplar READMEs in this domain:**
  - OCF quartz-solar: quick start code, Colab, install, model description, evaluation results, restrictions, dev setup — [GitHub](https://github.com/openclimatefix/open-source-quartz-solar-forecast).
  - windward: architecture and agent diagrams, data registry, results, tree, roadmap, cost — [GitHub](https://github.com/fborbon/windward).
  - hackout-26: 5-line quickstart including `pytest`, backtest and an API with `/docs` — [GitHub](https://github.com/Kr1sh-Parmar/hackout-26).
  - GEB HEFTcom24: env files, a data download guide, sequential scripts mapped to paper results — [GitHub](https://github.com/BigdogManLuo/HEFTcom24).
  - jbrowell/HEFTcom24: secrets in a git-ignored file, scheduled `auto_submitter.py` — [GitHub](https://github.com/jbrowell/HEFTcom24).

### Inferences
Synthesised checklist, derived from the sources above. Each item is traceable to the cited practices.

1. **Top of README (first screen):** one-sentence value proposition; a results table (MAE/RMSE/NMAE versus persistence and raw power-curve baselines, for 24–48 h); a demo GIF or screenshot; and a single copy-paste run command. (PwC item 5; judge DEV article; quartz layout.)
2. **One command from a fresh clone:** e.g., `make demo` / `python -m app run --date 2026-02-10`, or `docker compose up`. It should work offline on committed sample data, with an optional live fetch. Pin dependencies with a lockfile or exact `requirements.txt` and state the Python version. (SANKHYA, marvinoka4.)
3. **No hidden secrets:** a `.env.example` plus an env-var table (name, required?, default, purpose). An LLM key must be optional, with a deterministic fallback path so "failure to run" cannot occur without a key. (jbrowell git-ignored key pattern; the fallback is an inference.)
4. **Commit sample inputs and outputs:** cached Open-Meteo responses for the replay month and generated forecast CSVs and plots under `outputs/`. Judges can then see results without running anything. (PwC "pre-trained models"; repo-testify executes claims.)
5. **Evaluation command** that regenerates the results table: `python -m app evaluate`. (PwC items 3 and 5; quartz `scripts/run_evaluation.py`.)
6. **Architecture diagram as Mermaid** in the README (renders on GitHub), plus an agent-graph diagram with node responsibilities and routing conditions. (windward.)
7. **Data provenance section:** which Open-Meteo endpoint and model, how "as-of issue date" is guaranteed (previous_day1/2 or `&run=`), timezone (UTC vs Asia/Almaty), units and capacity normalisation. Plus a leakage statement. (Open-Meteo docs; HEFTCom realism lesson.)
8. **Limitations and honest failure modes:** a short replay window, 2 turbines, curtailment and downtime in actuals, NWP grid resolution in steppe terrain. (DEV judge; bjorko README.)
9. **"Where AI is used and why" table:** agent nodes/tools, what the LLM decides versus what the ML computes, and a traces or log example. (DEV judge "realistic AI integration"; windward.)
10. **Repo hygiene:** CCDS-like tree (`data/raw` immutable, `src/`, `notebooks/`, `outputs/`, `tests/`); a few fast `pytest` smoke tests; LICENSE; third-party data and licence disclosure (Open-Meteo CC BY 4.0 attribution; AGPL server code not vendored); a troubleshooting section (proxy, API rate limit, Windows paths). (CCDS; hackout-26 tests / `SOURCES.md`.)
11. **Pre-score the repo with an AI judge** (AI-Hackathon-Judge / repo-testify style) and fix whatever README commands fail in a clean environment. (Tool existence cited above.)

### Gaps
- No published description was found of how the specific hackathon's AI pre-scorer works. Assume it reads the README and tree, and possibly runs commands.
- Google/Microsoft ML project templates (e.g., Microsoft TDSP, Google "rules of ML") were not fetched in this session.
- Open-Meteo's exact licence and attribution wording (CC BY 4.0 for data) is based on prior knowledge, not re-verified in this session. Confirm on open-meteo.com/en/licence.
