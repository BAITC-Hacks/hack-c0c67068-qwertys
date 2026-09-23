# NWP-based day-ahead (24–48 h) wind power forecasting: physical, statistical and GBM methods, preprocessing, evaluation

Scope: methods compendium for an hourly 24–48 h forecast of two turbines 340 m apart in the Shelek corridor (KZ), using 10-min SCADA and ECMWF/GFS/ICON forecasts from Open-Meteo. The notes do not design a solution.

Source tags: **[bk]** means a classic reference cited from background knowledge. Its DOI/URL is given but was not re-fetched in this session, so treat exact numbers from these as "verify before quoting". Everything else was checked against the linked page, abstract or search-result snippet during this session (2026-09-23). Where only a search snippet was available, this is noted.

---

## 1. Pipeline taxonomy: physical vs statistical/ML vs hybrid, and what wins at day-ahead

### Takeaway
Beyond about 6 h, almost all skill comes from NWP. Time-series and persistence models add nothing at 24–48 h, so the practical choice is how to post-process NWP. Recent head-to-head studies find that "direct" (NWP→power ML) and "indirect" (NWP→hub wind MOS→power curve) chains perform about the same (<2 % difference). Much larger gains come from using **several NWP sources/grid points** (8–30 %) and from **turbine-level modelling** (10–15 %). The established answer is therefore a hybrid: a physically informed statistical/GBM MOS fed by multi-model NWP.

### Cited Findings
- **Classic taxonomy.** Giebel et al. (ANEMOS.plus, 2nd ed. 2011), "The State-of-the-Art in Short-Term Prediction of Wind Power: A Literature Overview", separates *physical* approaches (NWP downscaled to hub height, then a power curve; e.g. Prediktor, Previento) from *statistical* ones (direct learning NWP→power, e.g. WPPT), and describes most operational systems as combinations of the two — [DTU Orbit / DOI 10.11581/DTU:00000017](https://doi.org/10.11581/DTU:00000017) [bk]
- Pinson (2013, *Statistical Science* 28(4)) reviews forecasting challenges and the reliance on NWP beyond a few hours ahead — [arXiv:1312.6471](https://arxiv.org/pdf/1312.6471) [bk for content]
- **Direct vs indirect, multi-NWP, turbine vs farm level** (Yakoub, Mathew, Leal, *Heliyon* 2023, DOI 10.1016/j.heliyon.2023.e21479). Smøla wind farm, Norway: 68 turbines, 150.4 MW, 2017–2020.
  - NWP inputs: ECMWF-IFS (7.6 km, 2 runs/day), UKMO-EURO (3.05 km, 4/day), MEPS (2.5 km, 4/day).
  - Definitions. *Direct* maps weather parameters straight to power. *Indirect* first builds a downscaling model from NWP to **nacelle wind speed**, then converts that to power with performance curves.
  - Direct vs indirect: "negligible differences" (<2 %).
  - Using several NWP sources cut errors by 8–30 %.
  - Summing per-turbine models beat a single farm-level model by 10 % (RMSE) and 15 % (MAE).
  - Best scores: NRMSE ≈ 7.8–7.9 %, NMAE ≈ 4.5–4.7 % (aggregated turbine-level, mixed NWP).
  - The final blend weights each forecast by inverse squared recent RMSE.
  - [PMC10637996](https://pmc.ncbi.nlm.nih.gov/articles/PMC10637996/)
- **ECMWF HRES vs GFS** (Gobi, NW China, WRF–Transformer framework, 3 yr of operational wind-farm data): ECMWF beats GFS by about 3–4 % RMSE on average, and the gap widens with lead time. Multi-source NWP inputs reduced errors by 8–22 %. Search snippet only; full text returned 403 — [Renewable Energy 2026, S0960148126000881](https://www.sciencedirect.com/science/article/abs/pii/S0960148126000881)
- **Weather ensembles vs a single provider** (Bruninx et al., arXiv Feb/Jul 2026). Four years of Belgian offshore data.
  - Using an ensemble of weather forecasts from several providers instead of one improved point accuracy by **~17 % on average**.
  - Tree-based ML (conformalized quantile regression, NGBoost) clearly beat deterministic power-curve and calibrated-wake-model baselines.
  - A conditional diffusion model was best: −5 % MAE and −12 % CRPS versus the probabilistic baseline.
  - [arXiv:2602.13010](https://arxiv.org/abs/2602.13010)
- At day-ahead horizons, regional NWP (WRF) is described as outperforming both traditional statistical approaches and "direct data-driven AI models". AI is used mainly as post-processing in a GFS→WRF→AI chain. Search snippet — [Applied Energy 2025, S0306261925018008](https://www.sciencedirect.com/science/article/abs/pii/S0306261925018008)
- **NWP bias correction with SCADA, 48 h horizon** (Jonas et al. 2024). 65 × 2.1 MW onshore turbines, 2 yr of 10-min SCADA; NWP runs every 6 h with 72 h lead.
  - NWP bias depends on season (winter under-forecast, summer over-forecast) and time of day (daytime over-forecast, night under-forecast).
  - Per-turbine hybrid models cut RMSE versus the baseline (725 kW = 34.5 % NRMSE): GB by 28 % (to 519 kW, 24.7 %); NN/CNN/LSTM by 34–36 % (to about 462–477 kW, ≈22 %).
  - Architecture choice mattered little. Continuous learning (fine-tuning on new data) beat both frozen and from-scratch retrained models.
  - Separate per-turbine models were needed because of wake and maintenance differences.
  - [arXiv:2402.13916](https://arxiv.org/html/2402.13916)
- **GEFCom2014 wind track** used ECMWF u/v at 10 m and 100 m, hourly, for 10 Australian wind farms (2012–2013), scored with the quantile (pinball) score — [search summary of dataset descriptions, e.g. arXiv:2202.08524](https://arxiv.org/pdf/2202.08524); overview in Hong et al. 2016, IJF 32(3):896–913, [DOI 10.1016/j.ijforecast.2016.02.001](https://doi.org/10.1016/j.ijforecast.2016.02.001) [bk]
- **KDD Cup 2022 (Baidu SDWPF).** 134 turbines, 48 h ahead at 10-min resolution. It is a SCADA-only task with no NWP, so it is only partly relevant to NWP-driven day-ahead forecasting. Top solutions:
  - 88VIP combined a GBDT ("memorize the basic data patterns") with an RNN — [arXiv:2208.08952](https://arxiv.org/abs/2208.08952)
  - 3rd place used a single BERT/Transformer on wind speed and direction only, with post-processing to impose daily periodicity — [GitHub LongxingTan/KDDCup2022-WPF](https://github.com/LongxingTan/KDDCup2022-WPF)
  - Another team used LightGBM for 24–48 h and an LSTM for 0–24 h — [GitHub cdzhang/wind_power_forecast](https://github.com/cdzhang/wind_power_forecast)
  - Dataset paper: Zhou et al. 2022, [arXiv:2208.04360](https://arxiv.org/abs/2208.04360) [bk]
- **Reviews** (useful for citations in a write-up):
  - Hanifi et al. 2020, *Energies* 13(15):3764, [DOI 10.3390/en13153764](https://doi.org/10.3390/en13153764) [bk]
  - Wang Y. et al. 2021, "A review of wind speed and wind power forecasting with deep neural networks", *Applied Energy* 304:117766, [DOI 10.1016/j.apenergy.2021.117766](https://doi.org/10.1016/j.apenergy.2021.117766) [bk]
  - Sweeney, Bessa, Browell, Pinson 2020, "The future of forecasting for renewable energy", *WIREs Energy Environ.* 9:e365, [DOI 10.1002/wene.365](https://doi.org/10.1002/wene.365) [bk]
  - Tawn & Browell 2022, "A review of very short-term wind and solar power forecasting", *RSER* 153 — covers the minutes-to-hours regime, not day-ahead — [RePEc](https://ideas.repec.org/a/eee/rensus/v153y2022ics1364032121010285.html)
  - Hong et al. 2020, "Energy forecasting: a review and outlook", *IEEE OAJPE* 7:376–388, [DOI 10.1109/OAJPE.2020.3029979](https://doi.org/10.1109/OAJPE.2020.3029979) [bk]
  - ML reviews 2023–2025: [Discover Applied Sciences 2025](https://link.springer.com/article/10.1007/s42452-025-07675-x); [Energy Reports 2024](https://www.sciencedirect.com/science/article/pii/S2352484724003603); [Sustainability 2023](https://www.mdpi.com/2071-1050/15/14/10757)
- **IEA Wind Task 36 (and its successor Task 51)** Recommended Practice on Forecast Solution Selection has three parts: (1) selection process, (2) benchmarks and trials, (3) evaluation of forecasts and forecast solutions. It later became an Elsevier book (Möhrlen, Zack, Giebel) — [Task 36 RP page](https://iea-wind.org/task36/task36-publications/task36-recommended-practices/); [Task 51 RP page](https://iea-wind.org/task51/task51-publications/task51-recommended-practices/); [Part 1 PDF](https://iea-wind.org/wp-content/uploads/2021/04/IEAWindTask36-RecommendedPractice_Part1.pdf); [book](https://www.sciencedirect.com/book/monograph/9780443186813/iea-wind-recommended-practice-for-the-implementation-of-renewable-energy-forecasting-solutions)

### Inferences
- For 2 turbines with ~3 years of SCADA, "direct GBM on NWP features" and "indirect MOS-wind → empirical power curve" should land within a few % of each other (Smøla). A cheap hybrid is to feed the power-curve-transformed NWP wind **as a feature** into the GBM. That also protects against extrapolation in rare regimes.
- The biggest cheap wins are likely (a) ECMWF + GFS + ICON (+ neighbouring grid points and adjacent lead times) as inputs, and (b) per-turbine models or turbine-ID pooling. Architecture choice is secondary, which is consistent with Jonas et al. 2024.
- Persistence being "useless at 24 h" matches the literature. Persistence remains a required *reference* in the skill score, but climatology is the more informative baseline at 24–48 h (see §7).

### Gaps
- No verified quantitative head-to-head of physical vs ML chains specifically for mountain-pass or valley sites was found at day-ahead horizons.
- The full text of the Gobi ECMWF-vs-GFS paper was not accessible (403); only abstract-level numbers are available.
- GEFCom2014 per-team scores were not re-verified.
- HEFTCom2024 (GFS + ICON inputs; hybrid strategy paper [arXiv:2505.10367](https://arxiv.org/pdf/2505.10367)) is likely relevant but was not read.

---

## 2. Power curve modelling and SCADA cleaning (IEC binning, density, parametric/isotonic, curtailment/outage filters)

### Takeaway
Build the empirical power curve from **cleaned** data: remove outages, curtailment, stuck sensors and derates. Then use IEC-style 0.5 m/s binning (density-normalised wind) or a monotone fit (5-parameter logistic, isotonic, GAM) for the physical chain or as a GBM feature. OpenOA implements most filters and curve fits off the shelf. Air density matters at an elevated continental site. Stability also shifts the curve (up to ~15 %), which is one argument for letting a GBM learn residual dependence on shear/temperature.

### Cited Findings
- **IEC 61400-12-1 method of bins.**
  - Density-normalised wind: v_n = v · (ρ_t/ρ_0)^(1/3), with ρ_0 a reference such as 1.225 kg/m³ or the site mean — [arXiv:2304.09835 (XAI power-curve paper)](https://arxiv.org/pdf/2304.09835); [SkySpecs note](https://skyspecs.com/blog/a-study-on-air-density-air-density-normalization-using-remote-weather-data-for-scada-based-performance-analysis/)
  - The standard's 2017/2022 editions revised the air-density correction and the power-curve definition, and added interpolation to bin centre — [iTeh summary](https://standards.iteh.ai/catalog/standards/iec/b6b43db0-b0ba-41a0-baaa-2a027c60cc9b/iec-61400-12-1-2017); [IEC webstore](https://webstore.iec.ch/en/publication/26603)
- IEC air-density formula (Ed.1/Ed.2 annex):
  - ρ = (1/T)·[B/R_0 − φ·P_w·(1/R_0 − 1/R_w)]
  - R_0 = 287.05 J kg⁻¹K⁻¹ (dry air), R_w = 461.5 (water vapour), P_w = 2.05·10⁻⁵·exp(0.0631846·T) Pa, T in K, φ = relative humidity.
  - Dry-air version: ρ = B/(R_0·T).
  - Pitch-regulated turbines normalise wind speed; stall-regulated turbines normalise power, P_n = P·ρ_0/ρ — [IEC 61400-12-1](https://webstore.iec.ch/en/publication/26603) [bk]
- **OpenOA (NREL, open source) utilities**:
  - `power_curve.IEC`: 0.5 m/s bins by default, 0–30 m/s, bin means; missing bins linearly interpolated then forward-filled; power = 0 outside the cutoff range; optional linear interpolation between bin centres.
  - `logistic_5_parametric`: 5-PL fitted by least squares with scipy `differential_evolution`. Bounds for (a, b, c, d, g) = ((1200, 1800), (−10, −1e−3), (1e−3, 30), (1e−3, 1), (1e−3, 10)): a = upper asymptote in kW, b < 0 = slope, c = inflection wind speed, d = lower asymptote, g = asymmetry.
  - `gam`, and `gam_3param` (wind speed + direction + air density).
  - [OpenOA power_curve source](https://openoa.readthedocs.io/en/latest/_modules/openoa/utils/power_curve/functions.html); [OpenOA API](https://openoa.readthedocs.io/en/latest/api/utils.html)
- **5-PL functional form**: P(v) = d + (a − d) / [1 + (v/c)^b]^g, with b < 0 so that P→a as v→∞. This matches the OpenOA bounds. For normalised power, set a ≈ 1 and d ≈ 0 — form [bk], consistent with the [OpenOA bounds](https://openoa.readthedocs.io/en/latest/_modules/openoa/utils/power_curve/functions.html). Review of curve models (binning, polynomial, logistic, splines, ML): Lydia et al. 2014, *RSER* 30:452–460, [DOI 10.1016/j.rser.2013.10.030](https://doi.org/10.1016/j.rser.2013.10.030) [bk]
- **OpenOA filters** (`openoa.utils.filters`), from the [OpenOA API](https://openoa.readthedocs.io/en/latest/api/utils.html):
  - `range_flag`: outside [lower, upper].
  - `unresponsive_flag`: value unchanged for N consecutive intervals, i.e. **stuck sensors**.
  - `std_range_flag`: more than k·σ from the mean.
  - `window_range_flag`: flags value_col outside [min, max] while window_col is inside [start, end]. Classic use: wind 5–40 m/s but power < x % of rated, i.e. **outage/curtailment**.
  - `bin_filter`: bins by power, flags wind speeds more than a threshold from the bin median (std/scalar/MAD threshold, direction "all/above/below").
  - `cluster_mahalanobis_2d`: k-means + Mahalanobis distance.
  - The ENGIE example uses `bin_filter` with 100 kW power bins, a 1.5 m/s scalar threshold around the bin median, and bins from 20 kW up to about 90 % of rated — [OpenOA utils example](https://openoa.readthedocs.io/en/latest/examples/01_utils_examples.html)
- **OpenOA meteorology helpers** — [OpenOA API](https://openoa.readthedocs.io/en/latest/api/utils.html):
  - `compute_air_density`: ideal gas with humidity correction.
  - `air_density_adjusted_wind_speed`: the IEC correction.
  - `pressure_vertical_extrapolation`: p1 = p0·exp(−g·Δz/(R·T_avg)), useful to bring NWP surface pressure to hub height.
  - `compute_shear`: power-law α by OLS.
  - `extrapolate_windspeed`: v2 = v1·(z2/z1)^α.
  - `compute_u_v_components`, `compute_wind_direction`, `compute_turbulence_intensity`, `compute_veer`.
- **Outlier taxonomy and change-point + quartile cleaning** (Shen, Fu, Zhou, IEEE TSTE 2018/2019). Power-curve outliers fall into four types: bottom-stacked, mid-stacked and top-stacked outliers, plus scattered outliers around the curve. Stacked groups typically come from outages (P ≈ 0 at high wind), curtailment/derating (flat plateaus below rated) and sensor faults. Change-point grouping locates the gap between normal and abnormal data inside each wind-speed interval; a quartile (IQR) rule then removes scattered points — [IEEE Xplore 8330024](https://ieeexplore.ieee.org/document/8330024/). Bayesian change-point + quartile variant: [Wang, Liu, Wang 2023, Proc IMechE A](https://journals.sagepub.com/doi/abs/10.1177/09576509221119563)
- **Other cleaning methods in the literature**:
  - Hybrid iForest + DBSCAN; box-plot rule before DBSCAN to clarify stacked-outlier boundaries; KDE-based per-bin cleaning that does not assume a Gaussian — [Research Square 2024](https://www.researchsquare.com/article/rs-5288737/v1)
  - Isolation Forest + Mean Shift — [Energies 15(13):4918](https://doi.org/10.3390/en15134918)
  - Image/colour-space method — [Applied Energy 2022, S0306261922000733](https://www.sciencedirect.com/science/article/abs/pii/S0306261922000733)
  - Comparative anomaly-detection study for power-curve cleaning: Morrison, Liu, Lin, *Renewable Energy* 184 (2022) — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0960148121017134); [open PDF](https://eprints.gla.ac.uk/260595/1/260595.pdf)
  - Three-stage physics rules + regression + morphology — [arXiv:2504.21354](https://arxiv.org/pdf/2504.21354)
- Curtailment-aware curve refinement: Zhao Y. et al., "Data-driven correction approach to refine power curve of wind farm under wind curtailment", IEEE TSTE 9(1) 2018, [DOI 10.1109/TSTE.2017.2717021](https://doi.org/10.1109/TSTE.2017.2717021) [bk]
- **Rule-of-thumb abnormal-state rules from KDD Cup 2022/SDWPF**: treat as invalid when active power ≤ 0 while wind speed > 2.5 m/s, when pitch angle > 89°, or when direction values are physically impossible. Such rows were excluded from scoring — [SDWPF paper arXiv:2208.04360](https://arxiv.org/abs/2208.04360) [bk; verify thresholds]
- **Isotonic regression** (pool-adjacent-violators) gives a nonparametric monotone power curve: `sklearn.isotonic.IsotonicRegression(increasing=True, out_of_bounds="clip")` — [scikit-learn docs](https://scikit-learn.org/stable/modules/isotonic.html) [bk]
- **Stability shifts the curve.**
  - Power at a given hub wind speed is higher in stable and lower in strongly convective conditions, with average differences approaching ~15 % — Wharton & Lundquist 2012, *ERL* 7:014005, [IOP](https://iopscience.iop.org/article/10.1088/1748-9326/7/1/014005)
  - Regime-conditioned power curves differed most by stability (≈200 kW at 11 m/s), then turbulence intensity (91 kW), then shear exponent (32 kW at 10.5 m/s) — [Energy 2020, S0360544220321587](https://www.sciencedirect.com/science/article/abs/pii/S0360544220321587)
  - Review of stability estimation for wind power — [RSER 2022, S1364032122004099](https://www.sciencedirect.com/science/article/abs/pii/S1364032122004099)

### Inferences
- **Suggested cleaning order for the 10-min SCADA:**
  1. Physical range checks.
  2. Stuck values (e.g. identical wind or power for ≥ 3–6 consecutive 10-min records).
  3. Outage flag: P ≤ 0.01 while wind > cut-in + 1 m/s.
  4. Curtailment/derate flag: power plateau below 0.95 of rated while wind > rated; also a bin_filter / change-point pass.
  5. Aggregate to hourly only when ≥ 4–5 of the 6 records are valid.
  
  Flags should be kept as masks. Train the power curve on clean data only. For evaluation, decide explicitly whether curtailed hours are removed or kept (see §7).
- **Density at the site.** In the ISA standard atmosphere, ρ ≈ 1.112 kg/m³ at 1000 m vs 1.225 at sea level (−9 %). In a continental climate, T between −20 °C and +35 °C changes ρ by roughly ±10 % around the mean. A density-normalised wind (NWP T and surface pressure → hub-height ρ) is therefore a cheap, physically justified feature or correction.
- **Nacelle anemometer bias.** The nacelle anemometer sits behind the rotor, so its wind speed is biased relative to free stream (IEC 61400-12-2 uses a nacelle transfer function). Because the same sensor appears in train and test, this only matters if nacelle wind is used as an intermediate MOS target. The power target is unaffected.
- **Hourly vs 10-min curves.** The curve is convex below rated, so an hourly mean of P(v) ≠ P(mean v). A curve fitted on hourly averages is flatter, and it is the right one to use with hourly NWP. Alternatively, fit on 10-min data and add hourly wind variance.
- **Cut-out.** Isotonic or 5-PL fits do not handle cut-out (a power drop at about 20–25 m/s). Cap the monotone fit at the cut-out speed and handle that region with a rule or leave it to the GBM, if hourly means ever get that high at Shelek.

### Gaps
- The exact IEC 61400-12-1:2022 air-density formula changes were not verified; the standard is paywalled.
- Default thresholds of the OpenOA `window_range_flag` / `bin_filter` for this turbine class were not checked.
- No source was found on Shelek turbine models or hub heights.

---

## 3. NWP post-processing / MOS: bias correction, quantile mapping, direction-dependent, EMOS, AnEn, Kalman, multi-model, lagged runs, spatial neighbourhood

### Takeaway
Standard practice is a MOS layer trained on past forecasts at the **same lead time** against observations:
- linear or sector-wise regression, or a Kalman filter, for bias;
- EMOS/NGR or quantile regression for a calibrated distribution;
- analog ensembles for non-parametric uncertainty.

Multi-NWP blending and neighbourhood/lagged inputs are consistently among the largest gains. For power, post-processing the **final power** forecast matters more than post-processing only the weather inputs. Key data trap: Open-Meteo's *Historical Forecast* archive is stitched from the first hours of each run. It is not a 24–48 h lead-time dataset, and true fixed-lead archives (Previous Runs API) mostly start only in January 2024.

### Cited Findings
- **Kalman filter bias correction.** Cassola & Burlando 2012, *Applied Energy* 99:154–166, "Wind speed and wind energy forecast through Kalman filtering of NWP model output": recursive combination of observations and model forecasts to minimise bias, motivated by poor surface-wind skill in complex topography — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0306261912002747)
  - A KF bias correction of 72 h WRF hub-height wind forecasts reduced RMSE by 16 % and MAE by 14%. Attribution per search snippet — [PCMP 2021, "System bias correction of short-term hub-height wind forecasts using the Kalman filter"](https://pcmp.springeropen.com/articles/10.1186/s41601-021-00214-x)
  - Earlier classic: Louka et al. 2008, *J. Wind Eng. Ind. Aerodyn.* 96:2348–2362, [DOI 10.1016/j.jweia.2008.03.013](https://doi.org/10.1016/j.jweia.2008.03.013) [bk]
  - Scalar bias KF (as usually implemented [bk]):
    - state b_t = b_{t−1} + w, w ~ N(0, Q); observation e_t = y_t − x_t^NWP = b_t + v, v ~ N(0, R)
    - P⁻ = P + Q; K = P⁻/(P⁻ + R); b = b⁻ + K(e − b⁻); P = (1 − K)P⁻
    - corrected forecast = x^NWP + b
    - Run it separately per lead time / hour of day. The ratio Q/R sets the adaptation speed.
- **MOS origin**: Glahn & Lowry 1972, *J. Appl. Meteor.* 11:1203–1211 [bk] ([DOI 10.1175/1520-0450(1972)011<1203:TUOMOS>2.0.CO;2](https://doi.org/10.1175/1520-0450(1972)011%3C1203:TUOMOS%3E2.0.CO;2))
- **EMOS / NGR.**
  - Gneiting et al. 2005, *MWR* 133:1098–1118: Y ~ N(a + b·x̄, c + d·S²), fitted by minimum CRPS — [DOI 10.1175/MWR2904.1](https://doi.org/10.1175/MWR2904.1) [bk]
  - Wind speed version: Thorarinsdottir & Gneiting 2010, *JRSS A* 173:371–388, **left-truncated at 0** normal EMOS — [DOI 10.1111/j.1467-985X.2009.00616.x](https://doi.org/10.1111/j.1467-985X.2009.00616.x) [bk]
  - With deterministic multi-model inputs (ECMWF/GFS/ICON), x̄ and S² can be the multi-model mean and spread, i.e. a "poor man's ensemble" (inference).
- **Weather vs power post-processing.** Phipps, Lerch et al. compared four setups: raw, weather-only EMOS, power-only EMOS, and two-step. Post-processing the final power ensemble improved both calibration and sharpness. Post-processing only the weather ensemble "does not necessarily" improve power forecasts — [arXiv:2009.14127](https://arxiv.org/abs/2009.14127)
- **ML post-processing benchmarks** (weather): Rasp & Lerch 2018, *MWR* 146:3885 — distributional NN beats EMOS — [DOI 10.1175/MWR-D-18-0187.1](https://doi.org/10.1175/MWR-D-18-0187.1) [bk]. Schulz & Lerch 2022, *MWR* 150:235–257 — wind gusts; compares EMOS, QRF, GBM-EMOS, DRN, BQN — [DOI 10.1175/MWR-D-21-0150.1](https://doi.org/10.1175/MWR-D-21-0150.1) [bk]. Review: Vannitsem et al. 2021, *BAMS* 102:E681–E699, [DOI 10.1175/BAMS-D-19-0308.1](https://doi.org/10.1175/BAMS-D-19-0308.1) [bk]
- **Analog ensemble (AnEn).**
  - Method: for each lead time, find the past runs whose forecasts are most similar to the current forecast. The ensemble is the set of *observations* that verified those past forecasts — [Delle Monache publications](https://ldellemonache.scrippsprofiles.ucsd.edu/publications/)
  - Wind power application: Alessandrini, Delle Monache, Sperati, Nissen 2015, "A novel application of an analog ensemble for short-term wind power forecasting", *Renewable Energy* 76:768–781 — [publications list](https://ldellemonache.scrippsprofiles.ucsd.edu/publications/)
  - Similarity metric (Delle Monache et al. 2013, *MWR* 141:3498, [DOI 10.1175/MWR-D-12-00281.1](https://doi.org/10.1175/MWR-D-12-00281.1)) [bk]:
    - ‖F_t, A_t′‖ = Σ_{i=1..N_v} (w_i/σ_{f_i}) · sqrt( Σ_{j=−t̃..t̃} (F_{i,t+j} − A_{i,t′+j})² )
    - t̃ is typically 1, i.e. a ±1 h window; there are typically ~10–25 analogs; weights w_i are tuned per predictor (e.g. speed, direction, T).
  - Extensions: rare-event improvement — [MWR 147(7) 2019](https://journals.ametsoc.org/view/journals/mwre/147/7/mwr-d-19-0006.1.xml); ML-learned similarity metric — [arXiv:2103.04530](https://arxiv.org/pdf/2103.04530); day-ahead AnEn for wind-farm grid services (NREL) — [OSTI 1823425](https://www.osti.gov/biblio/1823425); AnEn as a predictability proxy — [Renewable Energy 2019](https://www.sciencedirect.com/science/article/abs/pii/S0960148119309668)
- **Multi-model blending.** Smøla combined forecasts with weights ∝ 1/RMSE² over recent hours, and multi-NWP cut errors 8–30 % — [PMC10637996](https://pmc.ncbi.nlm.nih.gov/articles/PMC10637996/). Combining ECMWF and GFS "clearly outperforms the better single model", and adding local observations helps at all horizons (search snippet) — [ETDEWEB 21002339](https://www.osti.gov/etdeweb/biblio/21002339). A multi-provider weather ensemble gave −17 % MAE — [arXiv:2602.13010](https://arxiv.org/abs/2602.13010). Classic: Nielsen et al. 2007, "Optimal combination of wind power forecasts", *Wind Energy* 10:471–482, [DOI 10.1002/we.237](https://doi.org/10.1002/we.237) [bk]
- **Spatial neighbourhood.** Andrade & Bessa 2017, *IEEE TSTE* 8(4):1571–1580, extract features from a **grid** of NWP points: spatial mean/std, PCA and temporal smoothing, fed to gradient-boosted trees. Reported MAE was about 12.85 % (wind) and 16.09 % (solar); these numbers come from a secondary summary in search results, not the paper itself — [ResearchGate](https://www.researchgate.net/publication/316355623_Improving_Renewable_Energy_Forecasting_With_a_Grid_of_Numerical_Weather_Predictions). Smøla's farm-level model used all NWP grid cells around the farm — [PMC10637996](https://pmc.ncbi.nlm.nih.gov/articles/PMC10637996/)
- **Open-Meteo archives (critical for leakage and lead-time alignment):**
  - The *Historical Forecast API* is built by **"stitching the first hours of each successive model run"**. Availability: ECMWF IFS HRES from 2017-01-01, GFS from 2021-03-23, ICON from 2022-11-24. Open-Meteo recommends the *Single Runs API* for studying lead-time degradation — [Open-Meteo Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api)
  - The *Previous Runs API* provides `_previous_day1` (value predicted 24 h before valid time) through `_previous_day7`. "Most models are archived from January 2024" (GFS 2 m T from March 2021) — [Open-Meteo Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api)
- **Direction-dependent / regime correction.**
  - A widespread practice in Chinese NWP-correction studies is to correct NWP wind speed toward measured hub-height wind (the "NWP wind speed correction" step) before the power model — e.g. [Frontiers Energy Res. 2024](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2024.1391692/full) (ResNet-GRU correction, 200 MW NW China); Yang et al. 2021, [IET RPG, corrected NWP + entropy combination](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/rpg2.12053); [dynamic analog matching with multi-source info, ESWA 2024](https://sciencedirect.com/science/article/abs/pii/S0957417424025910?via=ihub%3D)
  - Caveat: the Frontiers 2024 paper validates on only 7 days (25–31 Jan 2019), which is typical of weak evaluation in this literature — [Frontiers 2024](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2024.1391692/full)
- **Seasonal/diurnal NWP bias structure** in onshore NWP-to-SCADA wind — [Jonas et al. 2024](https://arxiv.org/html/2402.13916):
  - winter under-forecast / summer over-forecast;
  - daytime over-forecast / night under-forecast.

### Inferences
- **Quantile mapping** x′ = F_obs⁻¹(F_nwp(x)), per season, lead and direction regime, fixes the *distribution* of wind speed (e.g. the +0.5 m/s bias and a too-narrow/too-wide spread). It cannot fix timing or phase errors, which is what limits corr = 0.71, and it can increase MSE when correlation is low. Use it as an input transform or baseline, not as the final model.
- **Direction-conditional MOS.** For a bimodal E/W channelled corridor, a direction-conditional MOS (separate slope/intercept, or KF, for E and W regimes; or u/v interactions in a GBM) is the natural "physical" correction. NWP at 9–25 km cannot resolve the gap acceleration, so the speed-up factor per regime must be learned.
- **Lagged inputs.** With the Previous Runs API, each valid hour has day1 and day2 forecasts, i.e. two runs issued 24 h apart, from three models. That gives up to six members for a lagged multi-model "poor man's ensemble": use the mean/median and spread as features, or as EMOS inputs.
- **Short fixed-lead archive.** Because fixed-lead archives mostly start in 01/2024, training at the correct 24–48 h lead covers only ~2.7 years of the ~3-year SCADA record. Mixing in stitched short-lead historical forecasts for earlier years creates a train/test mismatch: they are more accurate than real day-ahead inputs. One option is to use them only for pre-training or power-curve fitting and to flag them with a "lead" feature.

### Gaps
- Could not verify exact ECMWF/GFS/ICON dissemination delays (the time a 00Z run becomes available) for the issue-time simulation.
- Could not verify the horizontal resolution of the ECMWF product Open-Meteo serves (open-data 0.25° vs 9 km HRES) for this location.
- No wind-power-specific quantile-mapping study was retrieved.
- The ETDEWEB multi-model result is abstract-level only.

---

## 4. Feature engineering for NWP→power models

### Takeaway
Core features:
- NWP speed at 80/100/120 m (and its cube or power-curve transform);
- u/v components or direction sin/cos;
- shear exponent from 10 m vs 100 m;
- stability proxies (T gradients, boundary-layer height, day/night);
- air density;
- cyclic hour and day-of-year;
- lead time;
- temporal smoothing and bidirectional lags (±1–3 h) of NWP to absorb timing errors;
- multi-model mean and spread.

The GEFCom2014 winner's key feature was bidirectionally lagged 100 m wind "energy" from ECMWF.

### Cited Findings
- **GEFCom2014 winner** (kPower; Landry et al., *IJF* 32(3) 2016): GBM multi-quantile regression, with each quantile and zone fitted independently.
  - Most prominent features: **bidirectional lagged 100 m wind energy forecasts**, i.e. values at t−k and t+k.
  - Smoothing was applied to the dominant input signal "to adapt to forecast inaccuracies".
  - A two-layer model used information from correlated farms.
  - The team won 11 of 12 tasks.
  - Search snippet; the page returned 403 — [ScienceDirect S0169207016000145](https://www.sciencedirect.com/science/article/abs/pii/S0169207016000145); [ResearchGate](https://www.researchgate.net/publication/299459109_Probabilistic_gradient_boosting_machines_for_GEFCom2014_wind_forecasting)
- GEFCom2014 inputs were **u10, v10, u100, v100** from ECMWF — [dataset summaries via search, e.g. arXiv:2202.08524](https://arxiv.org/pdf/2202.08524)
- **Meteorological conversions** (OpenOA `compute_u_v_components`, `compute_wind_speed` = √(u²+v²), `compute_wind_direction`, `compute_shear`, `extrapolate_windspeed` v2 = v1(z2/z1)^α, `compute_veer`) — [OpenOA API](https://openoa.readthedocs.io/en/latest/api/utils.html)
  - Meteorological convention [bk]: u = −V·sin(θ), v = −V·cos(θ), θ = 270° − atan2(v, u)·180/π (mod 360).
  - Shear exponent: α = ln(V₁₀₀/V₁₀)/ln(100/10).
- Shear exponent depends on roughness, stability, height and speed. Low-level jets (e.g. nocturnal) are the main cause of departures from the 1/7 power law — [search summary incl. Ocean Eng. 2022](https://www.sciencedirect.com/science/article/abs/pii/S0141118722002279); [Energy 2020](https://www.sciencedirect.com/science/article/abs/pii/S0360544220321587)
- Stability effect on the power curve is up to ~15 % — [Wharton & Lundquist 2012](https://iopscience.iop.org/article/10.1088/1748-9326/7/1/014005). This motivates stability proxies such as T₂ₘ − T₈₅₀, T at 80/120 m − T₂ₘ, surface sensible heat flux, BLH, and a night/day flag.
- **Diurnal and seasonal NWP bias** — [Jonas et al. 2024](https://arxiv.org/html/2402.13916) — which justifies hour-of-day and day-of-year cyclic encodings: sin(2πh/24), cos(2πh/24), sin(2π·doy/365.25), cos(2π·doy/365.25).
- **Spatial features**: grid mean/std/PCA over neighbouring NWP points — [Andrade & Bessa 2017](https://www.researchgate.net/publication/316355623_Improving_Renewable_Energy_Forecasting_With_a_Grid_of_Numerical_Weather_Predictions)
- **Multi-provider features**: an ensemble of weather providers gave −17 % MAE — [arXiv:2602.13010](https://arxiv.org/abs/2602.13010)
- **KDD Cup 2022, 3rd place**: only wind speed and direction as inputs, plus a daily-periodicity post-processing step — [GitHub](https://github.com/LongxingTan/KDDCup2022-WPF)

### Inferences
Suggested feature menu (all derived only from information available at issue time):
- **Hub-height wind proxies.** ws80, ws100, ws120 per model. Log-interpolation to a guessed hub height h, v_h = v₁₀₀(h/100)^α; since hub height is unknown, let the model choose via the 80/100/120 inputs. Also ws³ and PC(ws), the empirical power curve applied to NWP wind.
- **Direction.** u, v at 10 m and 100 m; sin/cos(wd); an E/W regime flag or learned sectors (8–16); the interaction ws × regime. For a channelled valley, the along-valley component (projection of (u, v) on the valley axis) is likely more informative than raw direction.
- **Stability and shear.** α(10–100) and α(80–120); T-gradient between levels; BLH if available; gust factor G = gust₁₀/ws₁₀ (a turbulence/mixing proxy); day/night flag.
- **Timing tolerance.** Rolling mean/std/min/max of NWP wind over ±1, ±3, ±6 h windows; lags and leads t±1, t±2 (the GEFCom trick); the NWP Δws over 1–3 h as a ramp indicator.
- **Multi-model.** Mean, median and std across ECMWF/GFS/ICON (and day1/day2 runs); pairwise differences (ECMWF − GFS) as a disagreement signal.
- **Thermodynamics.** ρ from NWP T and p (extrapolated to hub height); T₂ₘ for icing or low-temperature derates (e.g. T < −20 °C shutdowns); humidity and T near 0 °C as an icing flag.
- **Calendar and lead.** Hour, doy cyclic, and lead-hour, if leads 24–48 are pooled.
- **Do not use** SCADA lags inside the 24 h horizon. At 24–48 h, the last SCADA observation at issue time can serve only as a weak regime feature, and only with correct alignment.

### Gaps
- No source quantifying gust-factor or BLH feature gains for day-ahead wind power was retrieved.
- Open-Meteo variable availability (e.g. BLH, 850 hPa T) per model and per archive was not verified here.

---

## 5. Gradient boosting practice (LightGBM / XGBoost / CatBoost)

### Takeaway
GBMs are the default strong baseline for NWP→power tabular MOS:
- GEFCom2014 winner: GBM quantile regression;
- KDD Cup 2022: GBDT as a core component;
- Bruninx 2026: CQR and NGBoost built on trees.

Key choices:
- per-turbine vs pooled with a turbine ID;
- an L1/MAE objective when scored on NMAE (the MAE-optimal forecast is the median);
- `objective=quantile` for probabilistic output;
- optional monotone constraint on hub-wind features;
- clip to [0, 1];
- time-ordered early stopping.

### Cited Findings
- GEFCom2014 winner: independent GBM per quantile and per zone, bidirectional lagged 100 m wind-energy features, smoothing, two-layer multi-farm model — [Landry et al. 2016](https://www.sciencedirect.com/science/article/abs/pii/S0169207016000145)
- KDD Cup 2022, 88VIP: GBDT (base patterns) + RNN (latent transitions), final online score −45.213 — [arXiv:2208.08952](https://arxiv.org/abs/2208.08952). LightGBM used for 24–48 h and LSTM for 0–24 h — [cdzhang GitHub](https://github.com/cdzhang/wind_power_forecast). Another public KDD solution repo: [shaido987/KDD_wind_power_forecast](https://github.com/shaido987/KDD_wind_power_forecast)
- Per-turbine GB (100 stages, learning rate 0.05, depth 5) cut RMSE 28 % vs the NWP baseline at 48 h. NNs did slightly better (34–36 %). Per-turbine models were needed — [Jonas et al. 2024](https://arxiv.org/html/2402.13916)
- Tree-based probabilistic models (CQR, NGBoost) significantly reduced MAE vs power-curve and wake-model baselines — [Bruninx et al. 2026](https://arxiv.org/abs/2602.13010)
- Probabilistic GBDT with instance-based transfer learning on GEFCom2014 wind — [Energies 12(1):159](https://doi.org/10.3390/en12010159). Gradient-boosted quantile regression for wind power — [J. Mech. Sci. Technol. 2026](https://link.springer.com/article/10.1007/s12206-026-2102-z)
- Probabilistic LightGBM plus feature engineering in load forecasting (transferable practice) — [arXiv:2305.05575](https://arxiv.org/pdf/2305.05575)
- Boosting in energy research, systematic review — [arXiv:2004.07049](https://arxiv.org/pdf/2004.07049)
- **Library knobs** [bk] ([LightGBM parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html)):
  - LightGBM: `objective="quantile"` with `alpha=τ`; `objective="l1"` / `"huber"`; `monotone_constraints=[...]` with `monotone_constraints_method` ∈ {basic, intermediate, advanced}; `linear_tree=True` for piecewise-linear leaves (helps extrapolation on the steep part of the curve).
  - XGBoost ≥ 2.0: `objective="reg:quantileerror"` with `quantile_alpha=[...]`, plus `reg:absoluteerror`.
  - CatBoost: `loss_function="Quantile:alpha=τ"` or `"MultiQuantile:alpha=0.1,0.5,0.9"`.
- **Point forecast optimality** (Gneiting 2011, "Making and evaluating point forecasts", *JASA* 106:746–762, [DOI 10.1198/jasa.2011.r10138](https://doi.org/10.1198/jasa.2011.r10138)) [bk]: MAE is minimised by the median, RMSE by the mean. The training objective should match the scoring metric.

### Inferences
- **Hyperparameter starting ranges** (practitioner heuristics, not from a cited benchmark; ~20–25k hourly rows per turbine): `num_leaves` 15–63, `max_depth` 4–8, `learning_rate` 0.02–0.05, `n_estimators` up to 3000 with early stopping on a *later* time block, `min_data_in_leaf` 50–300 (large, because the target is noisy), `feature_fraction` 0.6–0.9, `bagging_fraction` 0.7–0.9 with `bagging_freq` 1, `lambda_l2` 0–10. Tune with time-series CV (§7), not random K-fold.
- **Monotonicity.** Constrain +1 on the hub-wind proxies (ws100, PC(ws)) only below cut-out. If the data contains cut-out/storm hours, either do not constrain or cap ws. Do not constrain direction, stability or time features.
- **Pooling vs per-turbine.** With two turbines 340 m apart in the same corridor, a pooled model with `turbine_id` (and possibly interactions with direction, since wake depends on direction along the E/W axis) doubles the data. Per-turbine models capture individual curves. Try both. The literature favours turbine-level granularity for accuracy (Smøla, Jonas), but pooling is a regularizer on small data.
- **Target handling.**
  - Normalised power in [0, 1]: clip predictions.
  - Many exact zeros (below cut-in, outages) and a mass at 1 (rated) make L2 poorly suited. L1 or quantile objectives are more robust.
  - An alternative is the generalised logit transform (Pinson 2012, *JRSS C* 61:555–576 [bk]; recent Bayesian version [arXiv:2505.06310](https://arxiv.org/html/2505.06310)): z = log(y^ν/(1 − y^ν)) on clipped y ∈ (ε, 1 − ε).
- **Two-stage "indirect" GBM.** GBM #1 predicts hourly nacelle wind (MOS); the empirical curve (IEC/isotonic) converts it to power. Run GBM #2 as a direct power model, then blend. This is Smøla's direct+indirect ensemble idea.

### Gaps
- No verified public GBM hyperparameters from GEFCom2014 or KDD top teams (the 88VIP PDF could not be parsed here).
- No study found that isolates the effect of monotone constraints on wind-power GBM accuracy.

---

## 6. Probabilistic forecasting: quantile regression, conformal prediction, intervals, reliability

### Takeaway
Wind-power uncertainty is strongly heteroscedastic: largest on the steep part of the curve (≈4–11 m/s), smallest near 0 and rated. Established tools, all implementable on top of a GBM:
- quantile regression (GBM with pinball loss; non-crossing via sorting);
- distributional GBMs (NGBoost);
- conformal calibration (split / CQR / EnbPI / ACI) to guarantee coverage.

Evaluate with pinball/CRPS plus reliability diagrams and sharpness.

### Cited Findings
- **Pinball (quantile) loss**: L_τ(y, q) = (y − q)(τ − 1{y < q}). It was the GEFCom2014 scoring rule, averaged over the 99 percentiles (τ = 0.01…0.99) — [Hong et al. 2016](https://doi.org/10.1016/j.ijforecast.2016.02.001) [bk]. Search confirms pinball/quantile-score evaluation for the wind track — [arXiv:2202.08524](https://arxiv.org/pdf/2202.08524)
- **Classic wind QR**:
  - Bremnes 2004, "Probabilistic wind power forecasts using local quantile regression", *Wind Energy* 7:47–54, [DOI 10.1002/we.107](https://doi.org/10.1002/we.107) [bk]
  - Nielsen, Madsen, Nielsen 2006, "Using quantile regression to extend an existing wind power forecasting system with probabilistic forecasts", *Wind Energy* 9:95–108, [DOI 10.1002/we.180](https://doi.org/10.1002/we.180) [bk]
  - Required properties (reliability, sharpness, resolution) and evaluation framework: Pinson et al. 2007, *Wind Energy* 10:497–516, [DOI 10.1002/we.230](https://doi.org/10.1002/we.230) [bk]
  - Paradigm "maximise sharpness subject to calibration": Gneiting, Balabdaoui, Raftery 2007, *JRSS B* 69:243–268, [DOI 10.1111/j.1467-9868.2007.00587.x](https://doi.org/10.1111/j.1467-9868.2007.00587.x) [bk]
- **Conformal prediction**:
  - EnbPI (Xu & Xie, ICML 2021): ensemble/bootstrap-based prediction intervals with approximately valid marginal coverage for non-stationary time series under mild assumptions; the first CP method designed explicitly for time series — [search summary](https://valeman.medium.com/demystifying-enbpi-mastering-conformal-prediction-forecasting-d49e65532416); original [arXiv:2010.09107](https://arxiv.org/abs/2010.09107) [bk]
  - Adaptive Conformal Inference (Gibbs & Candès 2021) updates the miscoverage level online under distribution shift — [arXiv:2106.00170](https://arxiv.org/abs/2106.00170) [bk]; AgACI variant — [Zaffran et al., arXiv:2202.07282](https://arxiv.org/pdf/2202.07282)
  - CQR (Romano, Patterson, Candès 2019): conformalize quantile-regression bands, giving heteroscedastic intervals with coverage guarantees — [arXiv:1905.03222](https://arxiv.org/abs/1905.03222) [bk]; used for offshore wind in [Bruninx et al. 2026](https://arxiv.org/abs/2602.13010)
  - Renewable-specific: context-aware conformal — [arXiv:2510.15780](https://arxiv.org/html/2510.15780); climate-invariant multi-horizon solar/wind conformal intervals — [arXiv:2607.11470](https://arxiv.org/html/2607.11470v1); multi-step dual-splitting CP — [arXiv:2503.21251](https://arxiv.org/pdf/2503.21251); CP survey for time series — [IEEE TPAMI 2023](https://dl.acm.org/doi/10.1109/TPAMI.2023.3272339)
  - Library: MAPIE (scikit-learn-contrib) — split/CV+/CQR regressors and a time-series regressor with EnbPI and ACI updates — [GitHub](https://github.com/scikit-learn-contrib/MAPIE) [bk]
- **NGBoost** (natural-gradient boosting of distribution parameters): Duan et al. 2020, [arXiv:1910.03225](https://arxiv.org/abs/1910.03225) [bk]. It was one of the three tree-based probabilistic methods in [Bruninx et al. 2026](https://arxiv.org/abs/2602.13010)
- The analog ensemble gives non-parametric predictive distributions directly from past observations — [Alessandrini et al. 2015 via publications list](https://ldellemonache.scrippsprofiles.ucsd.edu/publications/)

### Inferences
- **Recommended cheap stack.** LightGBM quantile models at τ ∈ {0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95} → sort to fix crossing (monotone rearrangement) → clip to [0, 1] → CQR calibration on the last held-out months, optionally stratified by predicted-power bin or direction regime, because coverage is conditional in practice.
- **Error shape.** The bounded [0, 1] target with point masses at 0 and 1 makes Gaussian intervals inappropriate. Quantile or conformal approaches avoid distributional assumptions.
- **Coverage drift.** Check coverage separately for E and W regimes and for seasons. Marginal coverage can hide regime-conditional under-coverage.

### Gaps
- No wind-specific benchmark comparing EnbPI vs CQR vs ACI at 24–48 h was retrieved.
- MAPIE's current (v1.x) API names were not verified this session.

---

## 7. Evaluation methodology: metrics, skill scores, significance, ramps, backtesting and leakage

### Takeaway
Report capacity-normalised NMAE/NRMSE and bias, per lead time and per regime, with skill scores vs **climatology** and persistence (and vs raw-NWP+power-curve). For probabilistic output, use pinball/CRPS plus reliability. Test differences with Diebold–Mariano. Backtest with rolling origin in strict issue-time order, using only NWP runs available at issue time and only lead-matched forecasts. IEA Task 36/51 stress fairness, repeatability, representativeness and metrics aligned with the use-case.

### Cited Findings
- **IEA Wind RP Part 3** (Evaluation of forecasts and forecast solutions):
  - Core principles are "fairness", "repeatability" and "representativeness".
  - Build a *framework* of metrics so that the performance criteria incentivise optimising the target variable that matters to the user.
  - The document covers MAE, RMSE and other attributes.
  - [search summary](https://www.academia.edu/99537832/IEA_wind_recommended_practices_for_selecting_renewable_power_forecasting_solutions_part_3_evaluation_of_forecasts_and_forecast_solutions); [Part 3 PDF](https://iea-wind.org/wp-content/uploads/2021/04/IEAWIND-TASK36_Recommended-Practice_Part3_20190228_v2-1.pdf); [Strathprints (Parts 2 & 3)](https://strathprints.strath.ac.uk/65917/); [hands-on examples paper, WIW 2023](https://iea-wind.org/wp-content/uploads/2024/10/WIW2023_092_IEAWindRPExmples_paper.pdf)
- **Messner, Pinson, Browell, Bjerregård, Schicker 2020**, "Evaluation of wind power forecasts — An up-to-date view", *Wind Energy* 23(6):1461–1481 — the modern reference for deterministic and probabilistic evaluation, proper scores and significance testing — [ResearchGate](https://www.researchgate.net/publication/339893948_Evaluation_of_wind_power_forecasts-An_up-to-date_view); DOI 10.1002/we.2497 [bk]
- **Classic standardisation protocol**: Madsen et al. 2005, *Wind Engineering* 29(6):475–489, [DOI 10.1260/030952405776234599](https://doi.org/10.1260/030952405776234599) [bk]. It defines [bk]:
  - NMAE = (1/N)Σ|ŷ − y|/P_inst
  - NRMSE = √((1/N)Σ(ŷ − y)²)/P_inst
  - NBIAS = mean(ŷ − y)/P_inst
  - the error decomposition, and the improvement vs a reference: Imp_ref = (E_ref − E)/E_ref · 100 %
  - reference models: persistence, climatology (mean) and the "new reference" ŷ_{t+k} = a_k·y_t + (1 − a_k)·ȳ, a_k = autocorrelation at lag k
- **Typical error levels**: day-ahead MAE "can be over 8 % of capacity" for smaller areas, with worst errors over 80 % of capacity; accuracy depends on regional capacity, dispersion and the model. Complex terrain is harder than flat terrain — [VTT, Nordic day-ahead error characteristics](https://cris.vtt.fi/en/publications/characteristics-of-day-ahead-wind-power-forecast-errors-in-nordic/). Smøla (flat-ish coastal, 68-turbine farm, multi-NWP, turbine-level) reached NMAE ≈ 4.5–5.6 %, NRMSE ≈ 7.8–9 % — [PMC10637996](https://pmc.ncbi.nlm.nih.gov/articles/PMC10637996/). Per-turbine 48 h NRMSE ≈ 22–25 % after correction (65 × 2.1 MW) — [Jonas et al. 2024](https://arxiv.org/html/2402.13916)
- **Probabilistic scores** [bk] (Gneiting & Raftery 2007, *JASA* 102:359–378, [DOI 10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437)):
  - CRPS(F, y) = ∫(F(x) − 1{x ≥ y})²dx = 2∫₀¹ L_τ(y, F⁻¹(τ))dτ. From K quantiles, approximate it as 2·mean_k L_{τ_k}.
  - Ensemble form: E|X − y| − ½E|X − X′|.
  - Interval (Winkler) score for a central (1 − α) interval [l, u]: IS = (u − l) + (2/α)(l − y)1{y < l} + (2/α)(y − u)1{y > u}.
  - Reliability diagram: observed frequency vs nominal τ. Also PIT histogram; PICP (coverage) and mean interval width for sharpness.
- **Diebold–Mariano test** (Diebold & Mariano 1995, *JBES* 13:253–263, [DOI 10.1080/07350015.1995.10524599](https://doi.org/10.1080/07350015.1995.10524599)) [bk]:
  - loss differential d_t = L(e₁ₜ) − L(e₂ₜ)
  - DM = d̄ / √(2π·f̂_d(0)/T), asymptotically N(0, 1); use a HAC variance with h−1 autocorrelation lags for h-step forecasts
  - small-sample correction: Harvey, Leybourne, Newbold 1997, *IJF* 13:281–291 [bk]
  - For hourly day-ahead, errors within the same issue day are strongly correlated, so compute DM on **daily-mean losses**.
- **Ramp metrics**:
  - Example definition: ΔP ≥ 50 % of capacity within ≤ 4 h. NREL's swinging-door algorithm extracts ramps by magnitude, rate and duration.
  - Ramp skill metrics: CSI, mean start/end time error (MSTE/METE), mean relative magnitude error.
  - Plain MAE/RMSE is ill-suited to ramps.
  - [search summary](https://journals.ametsoc.org/view/journals/wefo/31/4/waf-d-15-0144_1.xml); Ramp Tool & Metric (phase/duration/amplitude matching skill) — Bianco et al. 2016, *Weather Forecast.* 31(4); NREL ramp report — [NREL 61730](https://docs.nrel.gov/docs/fy14osti/61730.pdf); Belgian offshore ramp evaluation — [arXiv:2510.15474](https://arxiv.org/pdf/2510.15474)
- Open-source systematic validation framework for wind speed and power forecasts — [Renewable Energy 2022, S0960148122014707](https://www.sciencedirect.com/science/article/pii/S0960148122014707)
- **Backtesting**:
  - Rolling-origin evaluation: Tashman 2000, *IJF* 16:437–450, [DOI 10.1016/S0169-2070(00)00065-0](https://doi.org/10.1016/S0169-2070(00)00065-0) [bk]
  - CV for time series: Bergmeir & Benítez 2012, *Inf. Sci.* 191:192–213, [DOI 10.1016/j.ins.2011.12.028](https://doi.org/10.1016/j.ins.2011.12.028) [bk]
  - scikit-learn `TimeSeriesSplit(n_splits, gap=…, test_size=…)` supports gaps between train and test — [docs](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) [bk]
- **Lead-time alignment and data sources**: Open-Meteo's Historical Forecast API stitches first hours of runs, while the Previous Runs API gives true 24 h / 48 h lead values, mostly from 01/2024 — [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api); [Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api)
- **Short test windows are a pitfall.** Some published NWP-correction papers validate on 7 days only — [Frontiers 2024](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2024.1391692/full)

### Inferences
- **Leakage checklist:**
  1. Define issue time t₀ (e.g. D−1 10:00 local; Kazakhstan has used a single UTC+5 zone since 2024 [bk, verify]) and target hours D 00–23 → leads ≈ 14–38 h or 24–48 h depending on the operational definition.
  2. For each target hour, use only the latest NWP run whose data would have been available by t₀. Use `_previous_day1`/`_previous_day2`, or the Single Runs API, never stitched analysis-like data at test time.
  3. SCADA-derived features may use only data up to t₀.
  4. Fit scalers, power curves, quantile maps and KF states only on training data (or online and causally).
  5. Leave a gap (≥ 2 days) between train and test blocks, because 24–48 h targets overlap consecutive issue days.
  6. Do not tune hyperparameters on the final test year.
- **Representativeness.** Evaluate over at least a full year, or report per season, because wind regimes in a mountain corridor are seasonal. Report per-regime (E vs W vs calm) and per-lead errors.
- **Baselines to report:**
  - (i) climatology: hour-of-day × month mean/median power, or empirical quantiles for probabilistic;
  - (ii) persistence (as required, though expected to be poor);
  - (iii) raw ECMWF ws100 → empirical power curve (the "physical" baseline);
  - (iv) linear MOS.
  
  Skill scores: SS = 1 − E_model/E_ref.
- **Curtailment and outages.** Either exclude flagged hours from the scored set or score against "available power". The choice must be stated explicitly and applied identically to all models (IEA fairness principle).

### Gaps
- The IEA RP Part 3 PDF could not be parsed in this environment. Specific numeric recommendations (e.g. minimum evaluation length, exact treatment of missing data) could not be quoted, and the details attributed to it above are limited to the principles found in search summaries.
- Messner et al. 2020 content is cited from background knowledge; the full text was not read.

---

## 8. Complex terrain and valley channelling: NWP resolution effects and mitigation

### Takeaway
In gaps, passes and channelled valleys, global NWP (9–25 km) and even 1–3 km mesoscale models under-resolve terrain. Typical symptoms:
- speed-up magnitude errors (rotor-layer biases of up to ~2 m/s even at 1 km);
- errors in vertical mixing and low-level jets;
- direction-regime-dependent biases;
- diurnal thermally driven errors.

Timing and direction of regime onset are usually captured better than magnitude. That makes statistical, regime-aware MOS (or dynamic/CFD downscaling) the key lever, which fits the Shelek corridor's bimodal E/W pattern.

### Cited Findings
- **Altamont Pass** (Arthur et al., *Wind Energ. Sci.* 10:1187, 2025). Diurnal gap-flow speed-up events; WRF v4.4 at 1 km (vs HRRR 3 km), MYNN vs a new 3D PBL scheme.
  - Both captured the timing and SW direction of speed-ups reasonably well.
  - Rotor-layer winds were **overestimated by up to 2 m/s**, near-surface winds underestimated (insufficient downward momentum mixing).
  - Only 1–2 model levels below 30 m, so near-surface jets were missed.
  - Fractional bias: about +0.05 to +0.10 in the rotor layer, −0.15 to −0.20 near the surface. Monthly capacity factor was overestimated by 7–11 %.
  - Terrain remains under-resolved even at 1 km.
  - [WES 2025](https://wes.copernicus.org/articles/10/1187/2025/)
- Complex terrain is usually under-resolved in mesoscale NWP, even at 1 km or sub-km grids. Dynamic downscaling with a high-resolution (mass-consistent) wind model captures ridge speed-up, **valley channelling**, flow separation and thermally induced flows. Search snippet — [USFS WindNinja-type downscaling study](https://research.fs.usda.gov/treesearch/61477)
- Day-ahead multi-scale forecasting in complex terrain: 500 m NWP + microscale CFD — [Houhoku wind farm, Japan, SETA 2022](https://www.sciencedirect.com/science/article/abs/pii/S2213138822000479). With high-resolution NWP, deterministic CFD downscaling can match or beat ANN statistical downscaling at day-ahead — [J. Sol. Energy Eng. 142(3):034502](https://asmedigitalcollection.asme.org/solarenergyengineering/article-abstract/142/3/034502/1072085/Day-Ahead-Wind-Power-Forecast-Through-High). NWP+ANN coupling — [Energies 14(2):338](https://doi.org/10.3390/en14020338)
- **Complex-topography probabilistic deep learning, Arctic Norway** — [arXiv:2203.07080](https://arxiv.org/pdf/2203.07080). Physics-based ultra-short-term forecasting in complex terrain — [Energies 17(21):5493](https://doi.org/10.3390/en17215493). Digital twin of an onshore farm in complex terrain — [arXiv:2307.02097](https://arxiv.org/pdf/2307.02097)
- **NW China arid/Gobi** (a relevant analogue climate to SE Kazakhstan): ECMWF HRES beats GFS by 3–4 % RMSE, with the gap growing with lead time — [Renewable Energy 2026](https://www.sciencedirect.com/science/article/abs/pii/S0960148126000881). Terrain and NWP resolution cause systematic NWP-vs-site deviations, hence the Chinese "NWP wind speed correction" step — [Frontiers 2024](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2024.1391692/full)
- Kalman-filter bias correction was explicitly motivated by poor NWP surface-wind skill "especially in complex topography regions" — [Cassola & Burlando 2012](https://www.sciencedirect.com/science/article/abs/pii/S0306261912002747)
- Diurnal NWP bias (day over-, night under-forecast) at an onshore farm — [Jonas et al. 2024](https://arxiv.org/html/2402.13916). The same kind of pattern is expected where thermally driven valley winds dominate.

### Inferences
- **For the Shelek corridor.** A likely failure mode is that ECMWF gets the regime (E vs W, onset timing) partly right but not the channelled magnitude. The observed corr 0.71 and +0.5 m/s bias fit this picture.
- **Mitigations**, in order of effort:
  1. Direction/regime-conditional MOS (E vs W slopes and intercepts), or GBM with u/v and along-axis wind.
  2. Pressure-gradient-type features that drive gap winds: differences in NWP surface pressure between grid points on either side of the corridor, if multiple points can be pulled. Plus multi-point neighbourhood features. The 2-D grid approach of Andrade & Bessa is the tested analogue.
  3. Stability/diurnal features for thermally driven flows.
  4. Analog ensemble conditioned on regime.
  
  CFD/WRF downscaling is out of scope for a hackathon.
- **Wakes between the two turbines.** At 340 m apart (≈3–4 rotor diameters for ~90–110 m rotors), the downstream turbine in each regime will likely be waked for roughly one direction sector: E winds wake one, W winds the other. Expect turbine-specific, direction-dependent curves, which argues for per-turbine models or turbine_id × direction interactions.

### Gaps
- **No reliable sources found** on Dabancheng (Xinjiang) mountain-pass forecasting or on Kazakh wind farms (Shelek/Dzungarian Gate/Ereymentau), in English-language search this session. Searches in Chinese or Russian may be needed.
- No quantitative study found comparing 9 km ECMWF vs 2–3 km regional NWP errors specifically for gap-flow wind farms at day-ahead power level. The Altamont study covers only 1 km WRF vs HRRR-like physics.
