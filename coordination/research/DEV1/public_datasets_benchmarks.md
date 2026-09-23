# Public wind power SCADA and forecasting datasets and benchmarks (as of 2026-09-23)

Scope: a catalogue of public datasets and benchmarks the team can use as reference, pretraining, validation or comparison material for an hourly 24–48 h NWP-based forecast for 2 turbines in the Shelek corridor, Kazakhstan. Our data: 10-min SCADA with wind speed, normalized power (0..1) and ambient temperature, about 3 years.
Legend: **NWP = yes** means the dataset ships archived weather *forecasts*, not just measurements or reanalysis. Only NWP = yes datasets match our day-ahead setting directly.
Research method: web search and fetch, 2026-09-23. Several PDFs (Hong et al. 2016 IJF, Hodge et al. 2012, the SDWPF Sci Data PDF) could not be parsed, so some numbers come from abstracts or search snippets. Each such case is flagged.

---

## Q1. GEFCom2012 and GEFCom2014 wind tracks: where to download, format, winning results

### Takeaway
Both are the classic open **NWP-based day-ahead** wind benchmarks: hourly, ECMWF forecast winds, normalized power (0..1). They are the closest public analogue to our task. GEFCom2014 wind has 10 Australian farms, u/v at 10 m and 100 m, 2012–2013, and 99-quantile pinball scoring. The data is still downloadable from Tao Hong's Dropbox link, the IJF paper appendix and Kaggle (for GEFCom2012). The GEFCom2014 winner used per-quantile gradient boosting (GBM). For a point-forecast reference, one recent paper reports normalized MAE ≈ 0.108 and RMSE ≈ 0.160 on all 10 GEFCom2014 farms.

### Cited Findings
**GEFCom2014 – wind track**
- Data: wind power plus ECMWF weather data for **ten wind farms in Australia**, hourly. The weather variables are the zonal (u) and meridional (v) wind components **at 10 m and 100 m**, covering **2012–2013**. — [arXiv 2404.17276 (html)](https://arxiv.org/html/2404.17276v1)
- Official data citation / DOI: "GEFCom2014-wind and GEFCom2014-solar datasets are available at https://dx.doi.org/10.1016/j.ijforecast.2016.02.001". This is the appendix of Hong et al. 2016, *Probabilistic energy forecasting: GEFCom2014 and beyond*, IJF 32(3). — [arXiv 2404.17276](https://arxiv.org/html/2404.17276v1); [ScienceDirect abstract](https://www.sciencedirect.com/science/article/abs/pii/S0169207016000133)
- Direct download of the full zip: `https://www.dropbox.com/s/pqenrr2mcvl0hk9/GEFCom2014.zip?dl=0`. Wind data is in `GEFCom2014-W_V2.zip`, folder `Task 15/`. Tasks 1–14 are subsets of Task 15. — [IEA Wind Task 51 benchmarks page](https://iea-wind.org/task51/task51-information-portal/benchmarks/); [greenlytics/mqe-forecast README (via search)](https://github.com/greenlytics/mqe-forecast)
- Info pages: http://www.drhongtao.com/gefcom/2014 and http://blog.drhongtao.com/2016/07/datasets-for-energy-forecasting.html. The blog page is live but has no direct links in its text. — [IEA Task 51](https://iea-wind.org/task51/task51-information-portal/benchmarks/); [Hong blog](http://blog.drhongtao.com/2016/07/datasets-for-energy-forecasting.html)
- Scoring: the full predictive distribution is given as quantiles and evaluated with the pinball loss (quantile score). — [search summary of GEFCom2014 papers](https://robjhyndman.com/papers/gefcom2014.pdf)
- The 99-quantile / 15-task setup is well known, but I could not parse the IJF PDF to confirm it here. The provisional leaderboard weighted 12 evaluation weeks linearly ("the last week is weighted as 12 times the first week") and rated teams by % improvement over the benchmark. — [Hong blog, provisional leaderboard method](http://blog.drhongtao.com/2014/12/rating-ranking-provisional-leaderboard-gefcom2014.html)
- Wind track winners (announced 2015-10-25):
  1. Landry, Erlinger, Patschke, Varrichio (Eigen Analytics, USA)
  2. Nagy, Borbely, Simon, Barta (BME / DMLab, Hungary)
  3. E. Mangalova (Siberian State Aerospace Univ., Russia)
  4. Kolter, Juban, Ohlsson, Maasoumy (C3 Energy)
  5. Yao Zhang (Xi'an Jiaotong)

  — [Hong blog, GEFCom2014 winners](http://blog.drhongtao.com/2015/10/gefcom2014-winners.html)
- Winning method: gradient boosted machines for multiple quantile regression, each quantile and zone fitted separately. It had the lowest error in 11 of 12 tasks and was second in the remaining one. Paper: Landry et al., IJF 32(3):1061–1066, 2016. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0169207016000145) (via search abstract)
- Other top methods: linear quantile regression (Juban et al.) and analogues / k-NN (Mangalova & Shesterneva). — [search summary incl. ResearchGate kNN paper](https://www.researchgate.net/publication/300001155_K-nearest_neighbors_for_GEFCom2014_probabilistic_wind_power_forecasting)
- Deterministic reference on GEFCom2014 wind, all 10 farms: **MAE 0.108, RMSE 0.160** in normalized power units, i.e. about 10.8% / 16% of capacity. — [arXiv 2404.17276](https://arxiv.org/html/2404.17276v1)
- Data conflict: the IEA Task 51 page lists GEFCom2014 as "7 wind farms, 2009–2012". That is the GEFCom2012 description copied over. Primary sources say 10 farms, 2012–2013. — [IEA Task 51](https://iea-wind.org/task51/task51-information-portal/benchmarks/) vs [arXiv 2404.17276](https://arxiv.org/html/2404.17276v1)

**GEFCom2012 – wind track**
- Data: observed hourly wind generation for **7 wind farms**, plus ECMWF wind forecasts from +1 to +48 h, **2009–2012**. Files: `windpowermeasurements.csv` and `windforecasts_wf*.csv`. Sources: IJF supplementary data (S0169207013000745) and Kaggle (`https://www.kaggle.com/c/GEF2012-wind-forecasting`). — [IEA Task 51](https://iea-wind.org/task51/task51-information-portal/benchmarks/)
- An R package copy exists: `tscompdata::gefcom2012_wp` holds 7 hourly series (training data only; the test periods are NA). — [tscompdata docs](http://pkg.robjhyndman.com/tscompdata/reference/gefcom2012_wp.html)
- Task: predict hourly power at 7 farms up to **48 h ahead**; metric RMSE on normalized power. Winner: team **Leustagos** (1st on both public and private leaderboards) using time- and weather-derived features, GBDT and linear models. Their development log: forecasts plus lags gave RMSE 0.1685, adding seasonal features gave 0.16393. The final private score was not found. — [IJF paper, feature engineering approach (search abstract)](https://www.sciencedirect.com/science/article/abs/pii/S0169207013000836); [winner repo](https://github.com/lucaseustaquio/gefcom-2012-wind-track)
- Kaggle access needs a Kaggle account and acceptance of the competition rules to download. The competition page exists, but its leaderboard could not be fetched. — [Kaggle GEF2012](https://www.kaggle.com/competitions/GEF2012-wind-forecasting)

### Inferences
- GEFCom2014 wind is the best open analogue of our setup: normalized power (like our 0..1), hourly, day-ahead ECMWF 10 m / 100 m winds, and multi-year history. Its target is a whole wind farm, though, which smooths output compared with a single turbine.
- NMAE ≈ 10–11% and NRMSE ≈ 16% of capacity (farm-level, GEFCom2014, deterministic) is a sensible "competent model" reference. A single turbine in complex terrain should be expected to do worse.
- Useful sanity check: if our pipeline is run on GEFCom2014 with the same features, it should land near MAE ≈ 0.11. A result far better than that suggests leakage.

### Gaps
- Exact GEFCom2014 wind pinball scores for the winner and the benchmark: the IJF PDF and the OneDrive leaderboard (http://1drv.ms/1HpwubL) could not be read. One paper cites "winner 1.21%" average pinball, but it was unclear whether that refers to wind or solar, so it is not used.
- Final GEFCom2012 private-leaderboard RMSE: Kaggle leaderboard not retrievable.
- Long-term availability of the Dropbox link is not guaranteed (third-party hosting). The IJF appendix is the stable fallback.

---

## Q2. KDD Cup 2022 SDWPF (Baidu / Longyuan, 134 turbines): download, paper, metric, winners

### Takeaway
SDWPF is the largest open **turbine-level** 10-min SCADA dataset: 134 turbines, one Longyuan wind farm in China. There are two versions: `sdwpf_kddcup` (245 days, the competition data) and `sdwpf_full` (Jan 2020–Dec 2021). The full version is on Figshare under **CC BY-NC-ND 4.0**. It has **no NWP forecasts**; the competition was a pure SCADA 48 h (288-step) forecast scored as mean(RMSE, MAE) summed over turbines. The winning leaderboard score was −44.917 (HIK).

### Cited Findings
- Paper: Zhou et al., *SDWPF: A Dataset for Spatial Dynamic Wind Power Forecasting Challenge at KDD Cup 2022*. arXiv:2208.04360, v1 2022-08-08, **v2 2025-04-30**. The journal version is *Scientific Data* (2024), "SDWPF: A Dataset for Spatial Dynamic Wind Power Forecasting over a Large Turbine Array", https://www.nature.com/articles/s41597-024-03427-5. — [arXiv abs](https://arxiv.org/abs/2208.04360); [Sci Data](https://www.nature.com/articles/s41597-024-03427-5)
- Download: **Figshare `https://figshare.com/articles/dataset/SDWPF_dataset/24798654`**, with folders `sdwpf_kddcup` and `sdwpf_full`. The original Baidu AI Studio link (aistudio.baidu.com/aistudio/competition/detail/152/0/datasets) is the historical source. — [Figshare (search summary)](https://figshare.com/articles/dataset/SDWPF_dataset/24798654); [arXiv html](https://arxiv.org/html/2208.04360v2)
- `sdwpf_kddcup` files: `sdwpf_245days_v1.csv`, `sdwpf_baidukddcup2022_turb_location.csv` (relative positions) and final-phase test data. — [search summary of Figshare](https://figshare.com/articles/dataset/SDWPF_dataset/24798654)
- `sdwpf_full` files: `sdwpf_2001_2112_full.csv` (**Jan 2020–Dec 2021**, 24 months, >11.4 M records) and `sdwpf_turb_location_elevation.csv` (positions plus elevation). — [search summary citing Sci Data / Figshare](https://www.nature.com/articles/s41597-024-03427-5)
- Variables (13 columns): TurbID, Day, Tmstamp, Wspd (m/s), Wdir (°), Etmp (external temp, °C), Itmp (internal temp), Ndir (nacelle direction), Pab1–3 (blade pitch), Prtv (reactive power, kW), **Patv (active power, target, kW)**. 10-min sampling; the KDD version has 4,727,520 rows. — [arXiv 2208.04360v2 html](https://arxiv.org/html/2208.04360v2)
- Invalid-data rules used in scoring:
  - negative Patv is treated as 0;
  - "unknown" values when Patv ≤ 0 and Wspd > 2.5 m/s, or when any pitch angle > 89°;
  - "abnormal" values when Ndir is outside [−720°, 720°] or Wdir outside [−180°, 180°].

  — [arXiv html](https://arxiv.org/html/2208.04360v2)
- Metric: "the average of RMSE and MAE is used as the main evaluation score", computed per turbine over **288 steps (48 h)** and combined over turbines. GRU baseline: RMSE 47.08, MAE 37.56, **score 42.32**. — [arXiv html](https://arxiv.org/html/2208.04360v2)
- Scale: >2,400 registered teams (the Sci Data abstract says 2,400+; the 3rd-place repo says "out of 2490 teams"). — [Figshare/Sci Data summary](https://figshare.com/articles/dataset/SDWPF_dataset/24798654); [LongxingTan repo](https://github.com/LongxingTan/KDDCup2022-WPF)
- Official winners (leaderboard shows the negative of the score; higher is better).
  - Regular track:
    1. **HIK −44.91708** ([paper](https://baidukddcup2022.github.io/papers/Baidu_KDD_Cup_2022_Workshop_paper_0518.pdf))
    2. **trymore −44.9234** ([paper](https://baidukddcup2022.github.io/papers/Baidu_KDD_Cup_2022_Workshop_paper_1286.pdf), [code](https://github.com/hanhanliu/wpf22))
    3. **Teletraan −45.09478** ([code](https://github.com/LongxingTan/KDDCup2022-Baidu); BERT-based, [arXiv 2307.09248](https://arxiv.org/pdf/2307.09248))
  - PaddlePaddle track: trymore, zhangshijin (−45.13867) and EasyST (−45.17326).

  — [baidukddcup2022.github.io](https://baidukddcup2022.github.io/)
- Other published solutions: 88VIP (−45.213, [arXiv 2208.08952](https://arxiv.org/pdf/2208.08952)); BUAA_BIGSCity, 11th place, STGNN, −45.36026 ([arXiv 2302.11159](https://arxiv.org/pdf/2302.11159), [code](https://github.com/BUAABIGSCity/KDDCUP2022)). — [search results](https://github.com/BUAABIGSCity/KDDCUP2022)
- Licence: **CC BY-NC-ND 4.0** (non-commercial, no derivatives). — [arXiv html](https://arxiv.org/html/2208.04360v2)

### Inferences
- The top scores cluster tightly (−44.92 to −45.2). Without weather forecasts, 48 h-ahead skill saturates quickly. This matches our observation that power autocorrelation at 24 h is about 0.1.
- SDWPF is useful for (a) turbine-level data-cleaning rules (curtailment and stoppage flags, e.g. Patv ≤ 0 with Wspd > 2.5 m/s), (b) pretraining or testing a wind-speed→power mapping, and (c) showing that a pure autoregressive model cannot beat NWP at 24–48 h.
- NC-ND licence: fine for hackathon research and comparison. Do not redistribute modified data.

### Gaps
- Whether `sdwpf_full` includes ERA5 or any weather-model fields could not be confirmed. A search snippet mentions ERA5 in the Sci Data paper's discussion, but the full text could not be fetched (nature.com redirect; PDF not parseable).
- Turbine rated power is not stated in the parsed text, so normalized (% of capacity) SDWPF scores could not be computed.

---

## Q3. Open turbine or farm SCADA datasets (Kelmarsh, Penmanshiel, Hill of Towie, La Haute Borne, EDP, UEPS/UEBB, Kaggle, others)

### Takeaway
The best currently available open 10-min SCADA sets are the UK ones under CC-BY-4.0: Kelmarsh (6 turbines, 2016–2024, v4 on Zenodo), Penmanshiel (14 turbines) and Hill of Towie (21 turbines, 2016–2024, released 2025). **None includes NWP forecasts.** For day-ahead work they must be paired with archived NWP, e.g. Open-Meteo. **Engie La Haute Borne is offline**: the portal domain did not resolve on 2026-09-23; OpenOA still ships a 2-year sample. EDP's own portal is listed as unavailable, with a mirror on Open Net Zero.

### Cited Findings
**Catalogue table** (sources in the rows below)

| Dataset | Turbines / type | Res. | Period | NWP? | Licence / access | URL / DOI |
|---|---|---|---|---|---|---|
| Kelmarsh (Cubico, UK) | 6 × Senvion MM92 (12.3 MW) | 10-min SCADA + events, PMU, grid meter | 2016–end 2024 (v4, 2025-08-12) | No | CC-BY-4.0, open | 10.5281/zenodo.16807551 (supersedes 5841834, 7212475) |
| Penmanshiel (Cubico, UK) | 14 × Senvion MM82 (28.7 MW) | 10-min | 2016–mid 2021 (v0.0.2); newer version exists | No | CC-BY-4.0, open | 10.5281/zenodo.5946807 (concept); record 5946808 |
| Hill of Towie (RES/TRIG, Scotland) | 21 × Siemens SWT-2.3-VS-82 | 10-min, 655 vars, alarm logs, upgrade dates | Jan 2016–Aug 2024 | No | CC-BY-4.0, 12.6 GB | 10.5281/zenodo.14870023 |
| La Haute Borne (Engie, FR) | 4 × Senvion MM82 | 10-min, 34 signals × avg/min/max/std | 2009– (≈8 yrs) | No | **Portal offline**; OpenOA sample | OpenOA `examples/data/la_haute_borne.zip` |
| EDP (PT/ES onshore) | 4 turbines (T01, T06, T07, T11) + met mast | 10-min, 83 SCADA cols, 41 met cols, logs, 28 failures | 2016–2017 | No | EDP portal "currently unavailable"; mirror on Open Net Zero | opendata.edp.com; opennetzero.org |
| UEPS Pedra do Sal (BR) | 20 × Enercon E-44 (18 MW), hub 55 m | 10-min SCADA + 100 m IEC mast (5 cup levels + sonic) + LiDAR | Aug 2013–Jul 2014 | No | Zenodo, open | zenodo.org/records/1475197 |
| UEBB Beberibe (BR) | 32 × Enercon E-48, hub 75 m | same | Aug 2013–Jul 2014 | No | Zenodo, open | zenodo.org/records/1475197 |
| Kaggle "Wind Turbine Scada Dataset" (Turkey) | 1 turbine | 10-min; LV ActivePower, Wind Speed, Theoretical_Power_Curve, Wind Direction | end 2017–2018 | No | Kaggle login | kaggle.com/datasets/berkerisen/wind-turbine-scada-dataset |
| Kaggle "Wind Power Forecasting" (theforcecoder) | 1 "windmill" | ~10-min (unverified) | ~2.5 years (≈2018–2020) | No | Kaggle login | kaggle.com/datasets/theforcecoder/wind-power-forecasting |
| CARE to Compare (DE offshore, anonymized) | 9 and 22 turbines, 64 and 238 vars | 10-min | ~2 yrs | No | Zenodo | zenodo 10958774 |
| Norrekaer (DK) | 41 turbines, 3 vars | 10-min | 1.5 yrs | No | DTU data | 10.11583/DTU.19076756.v1 |
| Ørsted Anholt / Westermost Rough (offshore) | 111 / 35 turbines | 10-min | 2 yrs | No | **Application + NDA** | orsted.com offshore-operational-data |
| Sotavento (Galicia, ES) | 24 turbines (farm total) | 10-min | – | paper uses NWP | Mendeley | data.mendeley.com/datasets/vtsgxnwswn/1 |
| Zhangbei (Hebei, CN) | 12 turbines | 60-s | Mar 2014–Mar 2015 | No | IEEE DataPort (login) | ieee-dataport.org |

- Kelmarsh v4: 10-min SCADA and events from 6 Senvion MM92 turbines, 2016–end 2024, extracted from Cubico's Greenbyte system. About 3.7 GB of SCADA plus PMU (2023–2024) and grid meter data. CC-BY-4.0, DOI 10.5281/zenodo.16807551, published 2025-08-12; supersedes v1–v3. Companion: Penmanshiel 10.5281/zenodo.5946807. — [Zenodo 16807551](https://zenodo.org/records/16807551)
- Penmanshiel: 14 Senvion MM82 turbines (28.7 MW total); the v0.0.2 record (2022-02-07) covers 2016–mid-2021. The record page says a newer version exists. CC-BY-4.0. — [Zenodo 5946808](https://zenodo.org/records/5946808)
- Hill of Towie: 21 Siemens SWT-2.3-VS-82 turbines, Jan 2016–Aug 2024, 10-min statistics plus alarm logs, shutdown durations and AeroUp/TuneUp upgrade dates. 12.6 GB, CC-BY-4.0, v1.0.0 published 2025-03-28 by RES on behalf of TRIG. — [Zenodo 14870023](https://zenodo.org/records/14870023); [OpenWindSCADA](https://github.com/sltzgs/OpenWindSCADA)
- La Haute Borne: 4 Senvion MM82 turbines commissioned 2009-01-15. 136 columns (34 measurements × avg/min/max/std) every 10 min. Listed as "Offline" in OpenWindSCADA. My fetch of `opendata-renewables.engie.com` on 2026-09-23 failed with DNS **ENOTFOUND** (dead link). — [search summary](https://data.mendeley.com/datasets/vmyg4yp3s8/1); [OpenWindSCADA](https://github.com/sltzgs/OpenWindSCADA)
- OpenOA (the NREL, now NLR, operational-analysis library) ships **two years of La Haute Borne data** as `examples/data/la_haute_borne.zip` (`pip install "openoa[examples]"`). It has downloaders for hourly **ERA5 and MERRA-2** reanalysis. The repo moved to `github.com/NatLabRockies/OpenOA`. — [OpenOA docs/search](https://openoa.readthedocs.io/en/latest/examples/index.html); [OpenOA GitHub](https://github.com/NREL/OpenOA)
- EDP: 2016–2017, 4 turbines (T01, T06, T07, T11), 10-min UTC. SCADA has ~417k rows × 83 columns; met mast ~87.5k rows × 41 columns; event logs ~256k rows; 28 failure records. 8 xlsx files, 219 MB. Mirrored on Open Net Zero. — [Open Net Zero](https://www.opennetzero.org/energias-de-portugal-sa-edp/wind-farm-data); [Mendeley description](https://data.mendeley.com/datasets/zjxjnjp3xs/1). OpenWindSCADA notes EDP "currently unavailable; T09 removed". — [OpenWindSCADA](https://github.com/sltzgs/OpenWindSCADA)
- Brazil UEPS/UEBB: coastal NE Brazil, Aug 2013–Jul 2014, IEC-compliant 100 m met masts with 5 levels of cup anemometers plus a 3D sonic at 100 m, and 10-min SCADA for all turbines. UEPS: 18 MW, 20 × Enercon E-44 at 55 m; UEBB: 32 × Enercon E-48 at 75 m. — [Zenodo 1475197](https://zenodo.org/records/1475197)
- Kaggle Turkey dataset: one turbine in Turkey, one CSV with 5 columns (Date/Time, LV ActivePower kW, Wind Speed m/s, Theoretical_Power_Curve KWh, Wind Direction °), end-2017 to 2018, 10-min. — [Kaggle](https://www.kaggle.com/datasets/berkerisen/wind-turbine-scada-dataset); [search summary](https://github.com/jonathanwvd/awesome-industrial-datasets/blob/master/markdown/wind_turbine_scada_dataset.md)
- Kaggle theforcecoder: "two-and-half years of data for a windmill". — [Kaggle (search snippet)](https://www.kaggle.com/datasets/theforcecoder/wind-power-forecasting)
- Other items from OpenWindSCADA:
  - Fuhrländer (5 turbines, 5-min, 312 vars, EPL-2.0)
  - DSforWind farms (zenodo 5516552 and 5516554)
  - Dundalk IoT (1 turbine, 14 yrs, Mendeley tm988rs48k)
  - Small São Paulo turbine (zenodo 7348454)
  - SMARTEOLE wake-steering (zenodo 7342466)
  - Vestas V100 Loegtved (Kaggle)
  - Levenmouth (ORE Catapult, paid, about £2000)

  — [OpenWindSCADA](https://github.com/sltzgs/OpenWindSCADA)
- IEEE DataPort: Zhangbei (Hebei) wind farm, 12 turbines, 60-s SCADA, Mar 2014–Mar 2015. — [IEEE DataPort keyword page (search snippet)](https://ieee-dataport.org/keywords/wind-power)

### Inferences
- For our "2 turbines, 3 variables" case the closest open analogues are Kelmarsh, Penmanshiel and Hill of Towie. Use them to test the approach: resample to hourly, keep only wind speed, power and temperature, add archived NWP for the farm coordinates, and forecast 24–48 h. They are onshore, multi-year and CC-BY.
- The Kaggle Turkey single-turbine data is useful only for power-curve and cleaning demos. It has no NWP, covers only about one year, and its provenance is unclear.
- Brazil UEPS/UEBB are coastal trade-wind regimes, meteorologically unlike the Shelek corridor (a gap-flow / channelled wind regime). Their value is mainly the met-mast vertical profiles.

### Gaps
- "EDP Hack the Wind" (the 2018 EDP competition) was not specifically verified. It is presumably the same 2016–2017 EDP data with a failure-prediction task; not confirmed.
- Licences for UEPS/UEBB (Zenodo) and the Kaggle theforcecoder dataset (location often described as India; not verified) were not confirmed.
- The latest Penmanshiel version number and period (probably extended like Kelmarsh v4) were not verified.

---

## Q4. Datasets that include NWP or operational forecasts (the most relevant class for day-ahead)

### Takeaway
Public datasets that ship **archived NWP or operational forecasts together with power** are rare. The main ones:
- GEFCom2012/2014 (ECMWF)
- **HEFTcom2024** (Hornsea 1 offshore, 1.2 GW, DWD ICON-EU and NCEP GFS, 2020–2024, CC BY-type licences, 72.5 GB)
- **RE-Europe** (ECMWF + COSMO, 1,494 regions, 2012–2014, CC BY-NC)
- **NREL WIND Toolkit** forecasts (simulated, by request)
- **ARPA-E PERFORM** (5-min actuals plus probabilistic day-ahead forecasts for ERCOT/MISO/NYISO/SPP, no login)

The Chinese State Grid 2019–2020 set contains **on-site measured** meteorology, not forecasts.

### Cited Findings
- **HEFTcom2024** (Hybrid Energy Forecasting and Trading Competition, IEEE PES / Univ. Glasgow et al.):
  - Portfolio: Hornsea 1 (1.2 GW offshore wind) plus about 2.4 GW of solar.
  - Weather: DWD ICON-EU and NCEP GFS gridded forecasts, hourly, 4 runs per day, three years of historic and operational forecasts.
  - Task: day-ahead quantiles 10–90% per half-hour, scored by pinball score. Benchmark 53.58 MWh; winner SVK 22.18 MWh (and £88.88 M trading revenue).
  - Data: Zenodo https://doi.org/10.5281/zenodo.13950764 (paper says CC BY 4.0); quick-start code at https://doi.org/10.5281/zenodo.14180847.
  - Paper: IJF, DOI 10.1016/j.ijforecast.2025.10.005.

  — [arXiv 2507.01579 html](https://arxiv.org/html/2507.01579)
- The HEFTcom2024 Zenodo record (v1, 2025-01-10) has ICON-EU NetCDF files for Hornsea 1 (e.g. `dwd_icon_eu_hornsea_1_20200920_20231027.nc`, 230 MB), energy-data CSVs, forecasts, trades and pinball scores. Period 2020-09-20 to 2024-05-19, total 72.5 GB. Licences are mixed: BSC Open Data Licence, OGL v3, Sheffield Solar terms. — [Zenodo 13950764](https://zenodo.org/records/13950764)
- **RE-Europe**: aggregated wind and solar generation plus load, with ECMWF and COSMO forecasts from +1 to +91 h. Hourly, 1,494 European regions, 2012–2014, CC BY-NC 4.0, open zip at https://zenodo.org/record/35177. — [IEA Task 51](https://iea-wind.org/task51/task51-information-portal/benchmarks/)
- **NREL WIND Toolkit**: WRF-simulated generation at about 126,000 US sites, 5-min, 2007–2013. Forecasts (1, 4, 6 and 24 h ahead, at 1-h resolution) require a special request form. Bulk data is on OEDI (`nrel-pds-wtk` bucket), plus the Wind Toolkit API. — [IEA Task 51](https://iea-wind.org/task51/task51-information-portal/benchmarks/); [NREL/NLR wind-toolkit page (search)](https://www.nrel.gov/grid/wind-toolkit)
- Renaming: NREL has been rebranded **NLR (National Laboratory of the Rockies)**, with new domains `developer.nlr.gov` and `docs.nlr.gov`. Old nrel.gov links may redirect. — [NLR developer docs](https://developer.nlr.gov/docs/wind/wind-toolkit/central-asia-wind-download/)
- NREL Western and Eastern Wind Integration datasets: simulated, 10-min, 2004–2006. The Eastern set includes 4 h, 6 h and day-ahead forecasts (MASS/WRF). — [IEA Task 51](https://iea-wind.org/task51/task51-information-portal/benchmarks/)
- **ARPA-E PERFORM** (NREL): time-coincident load, wind and solar **actuals and probabilistic forecasts** at 5-min resolution for ERCOT, MISO, NYISO and SPP.
  - ERCOT: actuals 2017–2018, forecasts 2018. Other ISOs: actuals 2018–2019, forecasts 2019.
  - Stored as .h5 on AWS `s3://arpa-e-perform/`; OEDI submission 5772; no login.

  — [OEDI](https://data.openei.org/submissions/5772); [catalog.data.gov](https://catalog.data.gov/dataset/arpa-e-perform-datasets); [docs](https://github.com/PERFORM-Forecasts/documentation)
- A study on PERFORM ERCOT data (181 wind farms, ECMWF-based day-ahead, Feb–May 2018) found day-ahead forecast-error standard deviations of **0.135–0.268 (average ≈ 0.188) of capacity** per farm. — [arXiv 2409.16308](https://arxiv.org/html/2409.16308)
- **Chinese State Grid Renewable Energy Generation Forecasting Competition dataset** (Sci Data 2022):
  - Sites: 6 wind farms (30–200 MW) and 8 solar stations, in North, Central and Northwest China.
  - Data: 15-min, 2019–2020. Wind speed and direction at several heights (incl. hub), plus temperature, pressure and humidity at 1.5 m, **measured on site**.
  - Format and access: .xlsx, CC BY 4.0, Figshare https://figshare.com/articles/dataset/Solar_and_wind_power_data_from_the_Chinese_State_Grid_Renewable_Energy_Generation_Forecasting_Competition/17304221 (v4), plus GitHub.

  — [PMC9492786](https://pmc.ncbi.nlm.nih.gov/articles/PMC9492786/); [Sci Data](https://www.nature.com/articles/s41597-022-01696-6)
- AEMO (Australia) 5-min wind-farm generation, 2005–ongoing, with no NWP. A prepared 2012–2013 set is on Strathclyde Pure. — [IEA Task 51](https://iea-wind.org/task51/task51-information-portal/benchmarks/)
- NWP archives for pairing with any SCADA set (not datasets in themselves, but they are what makes day-ahead backtests possible):
  - Open-Meteo **Historical Forecast API** stitches the first hours of each model run into a continuous series. The docs list ECMWF IFS HRES 9 km "since 2017-01-01", IFS 0.25° since 2024-02-03, GFS since 2021-03-23, and ICON / ICON-EU since 2022-11-24.
  - The **Previous Runs API** gives fixed lead times (day 1 to day 7) from January 2024.

  — [Open-Meteo docs](https://open-meteo.com/en/docs/historical-forecast-api). Conflict: a search summary said IFS HRES only "from March 2024"; the docs page states 2017-01-01 for HRES 9 km. — [Open-Meteo](https://open-meteo.com/en/docs/historical-forecast-api)

### Inferences
- For a realistic day-ahead backtest, only the NWP = yes datasets (GEFCom, HEFTcom2024, RE-Europe, PERFORM) show the true "forecast-error-limited" accuracy. SCADA-only sets combined with reanalysis (ERA5) give optimistic results, because reanalysis is not a forecast.
- The Historical Forecast API stitches analysis-like first hours of each run. Using it as training features for a 24–48 h model is **optimistic, similar to reanalysis**. Honest D+1/D+2 evaluation needs the Previous Runs API (from 2024) or true lead-time archives.
- HEFTcom2024 is the most modern open example of an ICON/GFS day-ahead pipeline with pinball scoring. It is offshore and 1.2 GW, so absolute error levels are not comparable to 2 onshore turbines.

### Gaps
- The exact licence per file for the RE-Europe NWP fields was not re-verified (the IEA page says CC BY-NC 4.0).
- No open dataset combining **single-turbine** SCADA with **archived operational NWP** in a continental / steppe climate was found.

---

## Q5. TSO transparency platforms with public day-ahead wind forecasts (benchmarks for forecast-accuracy levels)

### Takeaway
ENTSO-E and several TSOs (Elia, Fingrid, Energinet, NESO) publish actual wind generation **and** their official day-ahead wind forecasts. These give free, up-to-date "operational-grade" accuracy references, but only at **regional or national** aggregation, where errors are much lower than for single turbines.

### Cited Findings
- ENTSO-E Transparency Platform, "Generation Forecasts for Wind and Solar – Day ahead [14.1.D]": TSOs must submit day-ahead wind forecasts at least once per 24 h, by 18:00 Brussels time. Data view: https://transparency.entsoe.eu/generation/r2/dayAheadGenerationForecastWindAndSolar/show. — [ENTSO-E knowledge base](https://transparency.entsoe.eu/content/static_content/Static%20content/knowledge%20base/data-views/generation/Data-view%20Generation%20Forecast%20-%20Day%20Ahead.html); [search summary](https://www.researchgate.net/publication/366119926_Wind_Power_Generation_Scheduling_Accuracy_in_Europe_An_Overview_of_ENTSO-E_Countries)
- A deep-learning model trained on 36 European bidding zones (2020–2024, 1.57 M hourly training observations) beat ENTSO-E TSO day-ahead onshore wind forecasts by **25.65% in RMSE, 26.56% in MAE and 25.69% in NMAE**. Published in npj Clean Energy, June 2026. — [npj Clean Energy](https://www.nature.com/articles/s44406-026-00036-6) (via search summary; full text blocked)
- ENTSO-E scheduling accuracy overview: onshore wind in Germany, Spain, France and Sweden had annual downward / upward regulation needs of 0.8–14.4% / 0.8–6.5% of yearly energy. Some countries exceeded 41% / 132%. — [ResearchGate: Wind Power Generation Scheduling Accuracy in Europe](https://www.researchgate.net/publication/366119926_Wind_Power_Generation_Scheduling_Accuracy_in_Europe_An_Overview_of_ENTSO-E_Countries)
- Open-data test against official TSO forecasts, Germany (DE-LU): TSO day-ahead onshore wind MAE was **1,274 MW** versus 2,296 MW for an Open-Meteo-based model. Offshore: 538 MW versus 865 MW. The authors note that the TSO forecast uses later information. — [GitHub batinkesc/day-ahead-forecasting-open-data](https://github.com/batinkesc/day-ahead-forecasting-open-data)
- Elia (Belgium): open-data wind production estimates and forecasts (intraday, day-ahead, week-ahead), dataset ods086. The Belgian offshore zone has 11 farms and 2,262 MW. — [Elia open data](https://opendata.elia.be/explore/dataset/ods086/table/); [arXiv 2510.15474](https://arxiv.org/html/2510.15474)
- Fingrid (Finland): open REST API (JSON/CSV/XLSX/XML).
  - Datasets: wind generation 15-min (dataset 75), forecast updated every 15 min (245), forecast updated once a day (246).
  - The 36-h forecast uses several weather providers.
  - Data before 2023-06-13 is hourly.

  — [Fingrid 245](https://data.fingrid.fi/en/datasets/245); [Fingrid 246](https://data.fingrid.fi/en/datasets/246); [Fingrid 75](https://data.fingrid.fi/en/datasets/75)
- Energinet (Denmark), Energi Data Service: day-ahead forecasts of on- and offshore wind for DK1/DK2. — [Energinet data catalog](https://en.energinet.dk/energy-data/data-catalog/); [search summary](https://arxiv.org/pdf/2209.02009)
- NESO (GB): "14 Days Ahead Wind Forecast" dataset. — [NESO data portal](https://www.neso.energy/data-portal/14-days-ahead-wind-forecasts/14_days_ahead_wind_forecast)
- WindDragon (France, RTE regional wind with ECMWF HRES, trained 2018–2019, tested 2020) reached national NMAE 7.7% for **1–6 h** horizons. This NMAE is normalized by **average generation**, not capacity. Persistence scored 17.3%. — [arXiv 2402.14385](https://arxiv.org/html/2402.14385v1)

### Inferences
- TSO forecasts show what state-of-the-art operational pipelines achieve at country scale. Their errors are several times smaller than single-site errors because of spatial smoothing (see Q7). **They should not be used as a target for 2 turbines.**
- The German DE-LU example suggests that a simple Open-Meteo-based pipeline is about 1.8× worse than the TSO. That gap is a useful reminder of the value of multi-NWP blending and more weather points.

### Gaps
- RTE (eCO2mix) and EirGrid (Smart Grid Dashboard) day-ahead wind forecast availability was not verified in this pass.
- Per-zone NMAE values from the npj Clean Energy 2026 paper could not be extracted (nature.com blocked).
- ENTSO-E API access is widely known to require free registration plus a security token. Not re-verified here.

---

## Q6. Time-series pretraining corpora, benchmarks and dataset surveys that contain wind power

### Takeaway
The main wind series in time-series foundation-model corpora are the Monash / AEMO "wind_farms" (339 farms, 1-min, 2019–2020) and LOTSA's `wind_farms_with_missing` and `wind_power`. A new dedicated benchmark, **WPBench (arXiv 2609.24444, 2026-09-21)**, unifies 26 public wind datasets. Two survey papers give broad dataset lists: Effenberger & Ludwig (Wind Energy 2022) and a 2026 *Renewable & Sustainable Energy Reviews* review.

### Cited Findings
- Monash TSF archive, "Wind Farms": minutely wind power for **339 Australian farms** from AEMO, 2019-08-01 to 2020-07-31. Available with missing values and with missing values filled by zero. DOI http://doi.org/10.5281/zenodo.4659727. Also "wind_4_seconds": one farm at 4-s resolution from 2019-08-01, 7,397,147 points. — [Monash TSF archive (search summary of arXiv 2105.06643)](https://arxiv.org/pdf/2105.06643); [forecastingdata.org](https://forecastingdata.org/)
- LOTSA (Moirai pretraining corpus, Salesforce) includes subsets `wind_farms_with_missing`, `wind_power`, `solar_power`, and others. It has 174 subsets (925 GB), Apache 2.0, "for research purposes only". The energy-only filtered copy is `DAG-UPB/lotsa_energy`. — [HF Salesforce/lotsa_data](https://huggingface.co/datasets/Salesforce/lotsa_data); [HF DAG-UPB/lotsa_energy](https://huggingface.co/datasets/DAG-UPB/lotsa_energy)
- **WPBench** (Zhu et al., ECNU / ZJU / Hikvision, arXiv 2609.24444, 2026-09-21):
  - 26 public datasets in four groups:
    - single-turbine univariate: Wind Farm A/B, Chalmers, Maelstrom 1–4
    - single-turbine multivariate: Yalova, Wind Farm Sites, Kaggle1, SCADA_Fault
    - multi-turbine univariate: Wind Farm C, AEMO, COSMO, ECMWF
    - multi-turbine multivariate: GEFCom2012/2014, Kelmarsh, Penmanshiel, SDWPF, UEPS, UEBB
  - Setup: look-back 576; horizons 12, 24, 72 and 144 steps; metrics nMAE, nRMSE, DTW and others.
  - Results: foundation models (TOTO, FactoST-UTP, TTM) had the best nMAE.
  - Paper licence CC BY-NC-ND 4.0; code URL not given in the fetched excerpt.

  — [arXiv 2609.24444](https://arxiv.org/html/2609.24444)
- GIFT-Eval (23 datasets, 144k series, 7 domains incl. Energy) is a general TSFM benchmark. Whether it contains a dedicated wind subset was not confirmed. ProbTS and BasicTS: no confirmed wind dataset. — [GIFT-Eval arXiv 2410.10393](https://arxiv.org/pdf/2410.10393); [ProbTS GIFT-Eval doc](https://github.com/microsoft/ProbTS/blob/main/docs/documentation/Gift_eval.md)
- Surveys and lists:
  - Effenberger & Ludwig, "A collection and categorization of open-source wind and wind power datasets", arXiv 2202.08524, Wind Energy 2022, DOI 10.1002/we.2766. It bills itself as "the largest up-to-date overview" of open wind power datasets. — [arXiv](https://arxiv.org/abs/2202.08524); [Wiley](https://onlinelibrary.wiley.com/doi/full/10.1002/we.2766)
  - "Datasets for wind energy forecasting applications: A comprehensive review and benchmarking perspective", RSER 2026 (S1364032126002406). It screened more than 1,400 articles (1,431 included) and found that only a minority of forecasting studies use openly accessible data. — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1364032126002406) (search summary; 403 on fetch)
  - Energies 2020, "Wind Farm and Resource Datasets: A Comprehensive Survey". — [MDPI PDF](https://mdpi-res.com/d_attachment/energies/energies-13-04702/article_deploy/energies-13-04702.pdf)
  - IEA Wind Task 51 benchmark list. — [IEA Task 51](https://iea-wind.org/task51/task51-information-portal/benchmarks/)
  - OpenWindSCADA curated list (GitHub). — [OpenWindSCADA](https://github.com/sltzgs/OpenWindSCADA)
- UniWind (arXiv 2607.01670, 2026) is a day-ahead model tested on 24 farms: Anhui 8, Shandong 7 and Shanxi 7 (proprietary, 15-min, 2023–2024, ECMWF / GFS NWP) plus Kelmarsh and Penmanshiel (2017–2021). No data or code URLs are given. — [arXiv 2607.01670 html](https://arxiv.org/html/2607.01670)

### Inferences
- The TSFM corpora (Monash, LOTSA) hold mostly **aggregated farm-level AEMO series without covariates**. They can serve for zero-shot baselines (e.g. Chronos, Moirai, TOTO on the power series). At 24–48 h, however, such univariate models cannot beat NWP-driven models, given our autocorrelation of about 0.1.
- WPBench horizons (at most 144 steps, i.e. 24 h at 10-min) and its mostly no-NWP setting make it a reference for "SCADA-only" skill, not for NWP day-ahead skill.

### Gaps
- WPBench code/data repository URL not found in the fetched text.
- The full dataset table of the RSER 2026 review is behind a 403. Access via institution or preprint needed.

---

## Q7. Typical accuracy levels for day-ahead wind power forecasts (single turbine vs farm vs region)

### Takeaway
Rough ladder of day-ahead errors (% of installed capacity):
- **Country or large region:** NMAE ≈ 2.5–6%; error std ≈ 4.5–12%.
- **Single area or small farm:** NMAE > 8%.
- **Individual wind farms with NWP:** NMAE ≈ 10–16%, NRMSE ≈ 15–21% (UniWind 2026; GEFCom2014 ≈ 10.8% / 16%).
- **Single turbines:** expected to be at least as bad as small farms. I found no clean published NMAE for single-turbine day-ahead in % of capacity.

For 2 turbines in the Shelek corridor, **NMAE of roughly 10–18% and NRMSE of roughly 15–25% of capacity** would be realistic. Values much below about 8% NMAE should be treated as suspicious (possible leakage).

### Cited Findings
- **Nordic TSO day-ahead** (Miettinen & Holttinen, Wind Energy 20(6):959–972, 2017, DOI 10.1002/we.2073):
  - average MAE by region: **5.7% of installed capacity**
  - smaller areas: **>8%**
  - all Nordic regions aggregated: **2.5%**
  - maximum errors: ~39.8% (regions), >80% (small areas), 13.5% (Nordic)
  - error reduction saturates at about 50,000 km² aggregation area

  — [VTT CRIS](https://cris.vtt.fi/en/publications/characteristics-of-day-ahead-wind-power-forecast-errors-in-nordic/)
- **International comparison of operational day-ahead errors** (Hodge, Lew, Milligan et al., NREL 2012). Error std as a fraction of capacity:
  - ERCOT σ = 0.1187
  - Finland 0.0751
  - Ireland 0.0827
  - Sweden 0.0603
  - Germany 0.0450

  — [KTH DiVA full text](https://kth.diva-portal.org/smash/get/diva2:575812/FULLTEXT01) (values from search snippet; PDF not parseable); [NREL 56130](https://docs.nrel.gov/docs/fy12osti/56130.pdf)
- **Farm-level day-ahead with NWP, 2026 state of the art** (UniWind; NMAE / NRMSE as % of rated capacity):

  | Region | NMAE | NRMSE | Best baseline |
  |---|---|---|---|
  | Shandong | 9.92% | 14.94% | XGBoost, 12.35% NMAE |
  | Shanxi | 12.80% | 17.29% | XGBoost, 14.99% NMAE |
  | Anhui | 10.39% | 14.52% | FusionSF, 14.77% NMAE |
  | **UK (Kelmarsh / Penmanshiel)** | **16.14%** | **20.99%** | 2DXformer, 21.87% NMAE |

  — [arXiv 2607.01670](https://arxiv.org/html/2607.01670)
- **GEFCom2014 farms** (hourly ECMWF, deterministic): MAE 0.108, RMSE 0.160 of capacity. — [arXiv 2404.17276](https://arxiv.org/html/2404.17276v1)
- **ERCOT, 181 farms, ECMWF day-ahead** (PERFORM data): per-farm error std 0.135–0.268 of capacity, mean about 0.188. About 5.5% of actual values are exactly zero. — [arXiv 2409.16308](https://arxiv.org/html/2409.16308)
- **Turbine-level vs farm-level** (Smøla, Norway, 68 turbines, ECMWF-IFS + UKMO + MEPS):
  - Intraday 2 h: farm-level NMAE 5.58% / NRMSE 9.22%; aggregated turbine-level NMAE 4.69% / NRMSE 7.97%.
  - Turbine-level aggregation improved MAE by about 16% and RMSE by about 14%.
  - Multi-NWP blending cut errors by 8–30%.
  - The authors expect day-ahead errors to be higher but "within a similar order of magnitude".
  - Source: Yakoub, Mathew, Leal, Heliyon 2023.

  — [PMC10637996](https://pmc.ncbi.nlm.nih.gov/articles/PMC10637996/)
- Two single turbines in southern Germany (1.5 MW each, ECMWF NWP, 15-min, 2019–2020, day-ahead):
  - Best nMAE: AutoWP 0.61–0.69; N-HiTS 0.66–0.73.
  - The OEM power curve on NWP wind: 0.67–0.94.
  - Power-curve methods fed by NWP wind beat autoregressive DL (DeepAR, N-HiTS, TFT).
  - **The normalization is evidently not by capacity** (probably by mean power), so these numbers are not comparable in % of capacity.

  — [arXiv 2412.00423](https://arxiv.org/html/2412.00423)
- National aggregation, short horizon (France, 1–6 h): NMAE 7.7% of **mean generation**; persistence 17.3%. — [arXiv 2402.14385](https://arxiv.org/html/2402.14385v1)
- KDD Cup 2022 (SDWPF, 48 h, no NWP): winner score 44.92, the sum over 134 turbines of (RMSE+MAE)/2, apparently in MW-scale units. The GRU baseline was 42.32 on the paper's own test split. — [baidukddcup2022](https://baidukddcup2022.github.io/); [arXiv 2208.04360](https://arxiv.org/html/2208.04360v2)
- A literature statement surfaced in search: "NRMSE should be within 13% of installed capacity for the first 6 hours, which can go up to 22% for 48 hours ahead". Its exact origin (a paper or a grid-code requirement) was not verified. — [search snippet associated with PMC10637996](https://pmc.ncbi.nlm.nih.gov/articles/PMC10637996/)

### Inferences
- Aggregation ladder, strictly ordered: region (NMAE 2.5–6%) < farm (≈10–16%) < turbine (≥ farm). Two turbines give almost no spatial smoothing. The team should expect errors near or above the UK small-farm UniWind level (NMAE ≈ 16%, NRMSE ≈ 21%). Complex channelled terrain (Shelek / Dzungarian-type gap winds) and a single NWP source push errors further up.
- A per-turbine day-ahead error std of about 0.19 of capacity (ERCOT farms) is consistent with NRMSE ≈ 20% at single sites.
- Recommended framing for the jury: report NMAE and NRMSE as % of rated capacity, plus skill versus two baselines, (a) climatology / diurnal mean and (b) the "raw NWP wind → OEM or empirical power curve" model. The German single-turbine study shows (b) is a strong baseline.
- KDD Cup inference, only valid if the rated power is about 1.5 MW (unverified): 44.9 / 134 ≈ 0.335 MW per turbine of (RMSE+MAE)/2, i.e. about 22% of capacity. That would be the 48 h no-NWP ceiling.

### Gaps
- No peer-reviewed number for **single-turbine** day-ahead NMAE in % of capacity was found. It is inferred from farm-level data.
- China's grid-code day-ahead accuracy requirements (commonly cited as an accuracy score based on 1 − RMSE/Cap) were not verified.
- Kazakhstan-specific forecast accuracy requirements (KEGOC / KOREM balancing-market rules) were not found.

---

## Q8. Public datasets from Kazakhstan or Central Asia

### Takeaway
**No public turbine- or farm-level wind generation dataset for Kazakhstan was found**, and no public KEGOC hourly wind-generation series was located. Usable open resources are meteorological or modelled:
- **NREL (NLR) Central Asia Wind Toolkit**: WRF v3.7, **year 2015**, 15-min, 3 km over Kazakhstan; winds at 80, 100 and 120 m; free API key required.
- **Global Wind Atlas** climatology.
- **Data in Brief 2019** Kazakhstan power-system dataset: synthetic hourly wind availability from met stations via Weibull transformation, CC BY 4.0.
- Global NWP archives such as Open-Meteo, for Shelek coordinates.

### Cited Findings
- NREL/NLR **Central Asia Wind Toolkit**:
  - Year: 2015 only.
  - Resolution: 3 km over Kazakhstan, 9 km over the surrounding region; native 15-min (15, 30 or 60 min selectable).
  - Variables: wind speed, direction and temperature at 80, 100 and 120 m; pressure at 0, 100 and 200 m.
  - Access: API key plus email. CSV limited to 10,000 requests per day, 1 per second, single point and year per request.

  — [NLR developer: Central Asia API](https://developer.nlr.gov/docs/wind/wind-toolkit/central-asia-wind-download/); [NREL RE Data Explorer Kazakhstan (search summary)](https://docs.nrel.gov/docs/fy19osti/74216.pdf)
- The RE Data Explorer for Central Asia was launched in 2016 with USAID support. It is used by KEGOC for planning and grid-integration studies. — [NREL fy19osti/74216 (search summary)](https://docs.nrel.gov/docs/fy19osti/74216.pdf); [OSTI 1558355](https://www.osti.gov/biblio/1558355)
- Assembayeva, Egerer, Mendelevitch, Zhakiyev, "Spatial electricity market data for the power system of Kazakhstan", Data in Brief 2019:
  - Network: 193 lines at 220–1150 kV.
  - Nodal demand for one summer and one winter week, at 2015 conditions.
  - Wind availability: **met-station wind speeds converted via Weibull distributions into hourly 0–1 availability per node**. Not measured wind farm output.
  - Sources: KEGOC, KOREM, HydroMetCenter, NASA.
  - Licence CC BY 4.0, https://doi.org/10.1016/j.dib.2019.103781.

  — [PMC6661261](https://pmc.ncbi.nlm.nih.gov/articles/PMC6661261/)
- Global Wind Atlas has a Kazakhstan area page and a World Bank Data360 dataset (climatological means, not time series). — [GWA Kazakhstan](https://globalwindatlas.info/area/Kazakhstan); [World Bank Data360 GWA](https://data360.worldbank.org/en/dataset/WB_GWA)
- ENERGYDATA.INFO (World Bank) has a Kazakhstan country filter. No wind-generation time series were confirmed there. — [energydata.info KAZ](https://energydata.info/dataset/?vocab_country_names=KAZ)
- Context: Shelek is described as a 300 MW onshore project in Almaty region and Yereymentau as 307.89 MW in Akmola. UNDP identified 9 potential sites with mean wind around 7.5 m/s at 80 m. — [Power Technology](https://www.power-technology.com/data-insights/top-5-onshore-wind-power-plants-in-development-in-kazakhstan/); [ERI](https://www.eurasian-research.org/publication/potential-of-wind-energy-in-kazakhstan/)
- Open-Meteo's Historical Forecast and Previous Runs APIs are global. They can supply ICON, GFS and ECMWF forecast archives for the Shelek coordinates (see Q4 for start dates and caveats). — [Open-Meteo docs](https://open-meteo.com/en/docs/historical-forecast-api)

### Inferences
- The NLR Central Asia WRF year (2015) does not overlap our ~3-year SCADA period, so it cannot serve as a training input. It can serve as a **climatological / terrain reference**: e.g. whether a WRF 3 km grid reproduces channelled winds near Shelek at 80–120 m, and its vertical shear, useful for extrapolating NWP 10 m / 100 m winds to hub height.
- Kazakhstan-specific day-ahead benchmarks do not exist publicly. The team's own results would be (to our knowledge) among the first reported for the region. Report them against generic references: farm-level NMAE ≈ 10–16%, the UK small-farm UniWind level ≈ 16%.

### Gaps
- No KEGOC or KOREM public hourly wind (or renewable) generation series was found. KEGOC publishes system data, but no machine-readable open wind series was located in this pass.
- No public met-mast time series from Kazakh wind sites (UNDP-era masts at Shelek or Yereymentau) was found.
- No Central Asian wind datasets were found on Kaggle, Zenodo or Mendeley. Uzbekistan and Kyrgyzstan were not specifically searched beyond wind-map providers.
