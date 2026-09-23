# Open-Meteo as a source of archived (as-issued) NWP forecasts for leakage-free wind-power backtests (state as of 2026-09-23)

Scope note: research done 2026-09-23. Sources are (a) the live open-meteo.com docs, read from their source in the website repo [open-meteo/open-meteo-website](https://github.com/open-meteo/open-meteo-website/tree/main/src/routes/en/docs); (b) GitHub issues in [open-meteo/open-meteo](https://github.com/open-meteo/open-meteo/issues); (c) the AWS open-data README and S3 bucket; (d) live API tests I ran on 2026-09-23 for the site (43.645150, 78.535604). Findings from those tests are labelled **[TEST]** and link the exact request URL. Anything I could not verify is listed under Gaps.

Site constants used in the tests: `latitude=43.64515&longitude=78.535604`. The ECMWF IFS 9 km / best_match grid cell returned is **43.620384, 78.47891, elevation 555 m**. That cell is about 5 km WSW of the turbines, and both turbines map to it.

---

## Q1. Endpoints: base URLs, semantics, availability, update frequency, caveats (incl. exact previous_dayN / Historical-Forecast / Single-Runs semantics)

### Takeaway
Three archive endpoints serve past forecasts, and they differ in what they store:
- **Historical-Forecast** stitches lead hours 0–5 of each run into one series. It behaves like an analysis, so it is not an as-issued forecast.
- **Previous-Runs** `_previous_dayN` returns, for each valid hour V, the value from the run initialised at floor6(V)−24·N h. Lead times are therefore 24N…24N+5 h for 6-hourly models. Coverage mostly starts Jan–Mar 2024; ECMWF IFS 9 km starts 2025-10-01.
- **Single-Runs** (`run=`) returns the full horizon of one run. It has ECMWF IFS HRES 9 km from 2024-03-14 and all other models only from 2026-04-02, because older data was deleted after corruption.

For Feb 2026, the only as-issued full runs are `ecmwf_ifs` (Single-Runs). Other models have only fixed-lead slices (Previous-Runs).

### Cited Findings

#### Endpoint catalogue (free tier; commercial = prefix `customer-` + `&apikey=`)
- Forecast: `https://api.open-meteo.com/v1/forecast`. Default 7 days, `forecast_days` 0–16, `past_days` 0–92, time starts 00:00 today. There are also model-specific pages (`/en/docs/ecmwf-api`, `gfs-api`, `dwd-api`, `ukmo-api`, `jma-api`, `kma-api`, `cma-api`, `bom-api`, `gem-api`, `meteofrance-api`, …) that call the same `/v1/forecast` endpoint with a `models=` preset — [Forecast docs](https://open-meteo.com/en/docs); [website source](https://github.com/open-meteo/open-meteo-website/tree/main/src/routes/en/docs)
- Historical Forecast: `https://historical-forecast-api.open-meteo.com/v1/forecast`. Same parameters as the Forecast API; data sits on "a different set of servers with access to a large storage system" — [Historical Forecast docs](https://open-meteo.com/en/docs/historical-forecast-api)
- Previous Runs: `https://previous-runs-api.open-meteo.com/v1/forecast`. Adds variables `<var>_previous_day0..7`. Example from the docs: `...?latitude=52.52&longitude=13.41&hourly=temperature_2m,temperature_2m_previous_day1&past_days=7&forecast_days=1` — [Previous Runs docs](https://open-meteo.com/en/docs/previous-runs-api)
- Single Runs: `https://single-runs-api.open-meteo.com/v1/forecast`. Same parameters as the Forecast API plus a required `run=YYYY-MM-DDTHH:MM` (UTC init time). Example: `...?latitude=52.52&longitude=13.41&run=2026-09-20T00%3A00&hourly=temperature_2m&models=ecmwf_ifs` — [Single Runs docs](https://open-meteo.com/en/docs/single-runs-api)
- Historical Weather (reanalysis): `https://archive-api.open-meteo.com/v1/archive`, with `start_date`/`end_date` required. Datasets:
  - ERA5 0.25°, from 1940, 5-day delay
  - ERA5-Land 0.1°, from 1950
  - ERA5-Ensemble 0.5°, 3-hourly
  - CERRA 5 km, Europe only, 1985–Jun 2021
  - ECMWF IFS 9 km, 2017→ ("assembled by Open-Meteo using simulation runs daily at 0z, 6z, 12z and 18z")
  - ECMWF IFS Assimilation Long-Window 9 km, 6-hourly, 2024→, 2-day delay

  Source: [Historical Weather docs](https://open-meteo.com/en/docs/historical-weather-api)
- Ensemble: `https://ensemble-api.open-meteo.com/v1/ensemble`. "You can retrieve up to three days of historical data" for members. Ensemble mean/spread are stored longer, "most available since March 2026" — [Ensemble docs](https://open-meteo.com/en/docs/ensemble-api); [Ensemble Mean docs](https://open-meteo.com/en/docs/ensemble-mean-api)
- Seasonal: `https://seasonal-api.open-meteo.com/v1/forecast`. Serves ECMWF SEAS5 plus EC46 (36 km, 51 members); the seamless product uses EC46 for 46 days and then SEAS5 — [Seasonal docs](https://open-meteo.com/en/docs/seasonal-forecast-api)
- Other endpoints:
  - Elevation `https://api.open-meteo.com/v1/elevation` (Copernicus GLO-90 DEM)
  - Geocoding (repo [open-meteo/geocoding-api](https://github.com/open-meteo/geocoding-api))
  - Air Quality, Marine, Flood, Climate
  - Satellite Radiation (solar only; not relevant for wind)
  
  Sources: [Elevation docs](https://open-meteo.com/en/docs/elevation-api); [open-meteo README](https://github.com/open-meteo/open-meteo)
- Metadata endpoint per model: `https://<prefix>.open-meteo.com/data/<model>/static/meta.json`. Fields:
  - `last_run_initialisation_time`
  - `last_run_modification_time`
  - `last_run_availability_time` ("time when the data is actually accessible on the API server")
  - `temporal_resolution_seconds`, `update_interval_seconds`, `data_end_time`

  Calls to it "are not counted toward daily or monthly request limits". Servers are eventually consistent: "wait an additional 10 minutes after the forecast update has been applied" — [Model updates page](https://open-meteo.com/en/docs/model-updates); [ModelMetaJson.swift](https://github.com/open-meteo/open-meteo/blob/main/Sources/App/Helper/File/ModelMetaJson.swift)

#### Historical Forecast API — how it is assembled
- Docs: "Each run's first few hours are stitched into a continuous hourly timeseries… Coverage starts around 2022… Not suitable for long time series due to model version changes" — [Historical Forecast docs](https://open-meteo.com/en/docs/historical-forecast-api)
- Patrick Zippenfenig (maintainer), 2026-03-06: "the historical data uses near-realtime data with hours 0-5 from run 0z. Hours 6-11 from run 6z, 12-17 from run 12z and 18-23 from run 18z." — [issue #1750](https://github.com/open-meteo/open-meteo/issues/1750)
- Maintainer on ML use: "this data is not ideal for ML training" because of train/serve skew (features at lead 0–5 h vs lead 24–48 h in production) — [issue #1747](https://github.com/open-meteo/open-meteo/issues/1747)
- Per-model start dates (Historical Forecast):

  | Model(s) | Start date |
  |---|---|
  | ECMWF IFS HRES 9 km | 2017-01-01 |
  | ECMWF IFS 0.4° | 2022-11-07 |
  | ECMWF IFS 0.25° | 2024-02-03 |
  | ECMWF AIFS 0.25° Single | 2025-02-20 |
  | GFS 0.11° and GFS pressure variables 0.25° | 2021-03-23 |
  | NCEP AIGFS / HGEFS | 2026-01-07 |
  | DWD ICON / ICON-EU / ICON-D2 | 2022-11-24 |
  | UKMO Global 10 km | 2022-03-01 |
  | ARPEGE World | 2024-01-02 |
  | JMA GSM | 2016-01-01 |
  | GEM Global | 2022-11-23 |
  | CMA GRAPES | 2023-12-31 |
  | BOM ACCESS-G | 2024-01-18 |
  | KNMI/DMI | 2024-07-01 |
  | MeteoSwiss | 2025-07-29 |

  Source: [Historical Forecast docs](https://open-meteo.com/en/docs/historical-forecast-api)
- **[TEST]** At the site, the Historical-Forecast `ecmwf_ifs` values for 2026-02-01 00–06 UTC (1.55, 0.81, 2.27, 5.13, 5.92, 3.74, 3.16 m/s at 100 m) equal leads 0–5 of the 2026-02-01T00Z single run followed by lead 0 of the 06Z run. They are also identical to `wind_speed_100m` (previous_day0) — [test URL](https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=ecmwf_ifs&hourly=wind_speed_100m,boundary_layer_height&start_date=2026-02-01&end_date=2026-02-01&wind_speed_unit=ms)

#### Previous Runs API — exact definition of `_previous_dayN`
- Docs: "`_previous_day0` is the current model run (equivalent to the live Forecast API). `_previous_day1` is the value that was predicted 24 hours before valid time, `_previous_day2` 48 hours before, and so on up to day 7. For local models with shorter forecast horizons (2–5 days), only offsets within that horizon are populated." Global models update every 6 h and regional ones every 1–3 h. The docs say it supports "the same models as the Weather Forecast API" — [Previous Runs docs](https://open-meteo.com/en/docs/previous-runs-api)
- Maintainer's exact definition: "The 'previous_day1' uses then hours 24-29 from run 0z. Hours 30-35 from run 6z, 36-41 from run 12z and 42-47 from run 18z." — [issue #1750](https://github.com/open-meteo/open-meteo/issues/1750)
- **[TEST] Empirical confirmation for `ecmwf_ifs` at the site.** Every hourly `previous_dayN` value for 2026-02-01..02 matched, exactly, a Single-Runs value. For valid time V, dayN = run init floor6(V) − 24·N h, with lead 24N+0…24N+5 h. Examples:
  - V=2026-02-01T00 → d1 from 01-31T00Z (+24 h), d2 from 01-30T00Z (+48 h), d3 from 01-29T00Z (+72 h)
  - V=2026-02-01T23 → d1 from 01-31T18Z (+29 h), d2 from 01-30T18Z (+53 h)

  So `previous_day1` is a mix of four different runs within each UTC day, not the forecast of one issue time.

  Source: [prev-runs URL](https://previous-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=ecmwf_ifs&hourly=wind_speed_100m,wind_speed_100m_previous_day1,wind_speed_100m_previous_day2,wind_speed_100m_previous_day3&start_date=2026-02-01&end_date=2026-02-02&wind_speed_unit=ms) vs [single-run URL pattern](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=ecmwf_ifs&hourly=wind_speed_100m&run=2026-01-31T00:00&forecast_days=16&wind_speed_unit=ms)
- **[TEST] Anomaly.** For V=2026-02-01T18–23, `previous_day3` came from the 2026-01-29T12Z run (+78…83 h) instead of the 18Z run, even though the 01-29T18Z single run exists. It looks like a fallback to an older run when a run was not ingested into Previous-Runs. The effective lead can therefore occasionally be longer than 24N+5 h — same test URL as above.
- Availability: "Most models are archived from January 2024. Some models were added to the archive later in 2024 or 2025… GFS 2 m temperature — available from March 2021; JMA GSM and MSM — available from 2018. Additional historical coverage can be reconstructed on request" — [Previous Runs docs](https://open-meteo.com/en/docs/previous-runs-api)
- The docs' variable picker lists `_previous_dayN` for surface variables and for wind at 10/80/100/120/180/200 m — [previous-runs options.ts](https://github.com/open-meteo/open-meteo-website/blob/main/src/routes/en/docs/previous-runs-api/options.ts). Pressure-level `_previous_dayN` is not supported: **[TEST]** `wind_speed_850hPa_previous_day1` → HTTP 400 "Cannot initialize SurfacePressureAndHeightVariable… from invalid String value" — [test URL](https://previous-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=gfs_global&hourly=wind_speed_850hPa_previous_day1&start_date=2026-02-01&end_date=2026-02-01)
- Query by date range with `start_date`/`end_date` (a larger `past_days` was fixed in 2025) — [issue #1393](https://github.com/open-meteo/open-meteo/issues/1393)

#### Single Runs API — `run=` semantics, models, since when
- "`&run=` … specifies the model's initialisation time — the UTC reference time at which the observations are taken — not the time at which the forecast output becomes publicly available… typically 4–6 hours for global models… 1–3 hours for regional models." The time "must correspond to a valid run cycle… Runs that are not available will return an error." "Data is served from a dedicated archive storage system, so response times may be higher" — [Single Runs docs](https://open-meteo.com/en/docs/single-runs-api)
- Availability table:
  - ECMWF IFS HRES 9 km (O1280), hourly, 10-day horizon, 4× daily, **available from 2024-03-14 ("IFS Cycle 49R1 hindcasts")**. "From May 12, 2026 06 UTC, runs use the updated IFS Cycle 50R1."
  - "Others: up to 1 km, up to 15 minutely, up to 16 days, **2026-04-02**."
  
  Source: [Single Runs docs](https://open-meteo.com/en/docs/single-runs-api)
- Why other models start 2026-04-02: "Due to data corruption we removed data prior April 2nd from the single runs API. Use ECMWF IFS HRES to access a longer archive." On backfill: "We are preparing to download more single runs from GFS. No ETA yet. For other local domains it is not possible" (2026-07-10) — [issue #1969](https://github.com/open-meteo/open-meteo/issues/1969)
- Earlier statements, now superseded:
  - Mar 2026: "We have started storing the full forecast horizon since September 2025" — [issue #1747](https://github.com/open-meteo/open-meteo/issues/1747)
  - June 2025: storing all runs "will generate 300TB per 1 year" — [issue #1374](https://github.com/open-meteo/open-meteo/issues/1374)
  - July 2024: "Open-Meteo does not store individual runs" — [issue #897](https://github.com/open-meteo/open-meteo/issues/897)
- Blog announcement (2026-05-15):
  - full horizon of individual runs for "research post-processing AI/ML and backtesting"
  - supports bounding boxes (max 1000 grid cells), which are not compatible with `best_match`/seamless
  - "Over the coming months, we'll be integrating additional historical data from other weather models such as GFS and HRRR"
  - free tier has the same rate limits; commercial "API Professional" from €99/month
  
  Source: [Substack: Single Runs API](https://openmeteo.substack.com/p/single-runs-api)
- **[TEST] Behaviour for `ecmwf_ifs` at the site:**
  - `run=2024-03-13T00:00` → 400 "The requested model run is not available"; `run=2024-03-14T00:00` → OK
  - 2024-03-14 … ~2024-11-11: only 00Z/12Z runs (06Z → 400), horizon 240 h (lead 0–240 non-null)
  - From 2024-11-12: 4 runs/day. 00Z/12Z → 360 h (lead 0–360); 06Z/18Z → 144 h (lead 0–144; rest null)
  - Runs sampled 2024-06-01, 2024-11-12, 2025-03-01, 2025-06-15, 2025-09-30, 2025-10-01, 2026-01-31, 2026-02-15, 2026-05-12 and 2026-09-23 all existed
  
  Test URLs: [2024-03-14 run](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&run=2024-03-14T00:00&models=ecmwf_ifs&hourly=wind_speed_100m); [2024-06-01T06 → 400](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=ecmwf_ifs&hourly=wind_speed_100m&run=2024-06-01T06:00); [2026-01-31T18 (144 h)](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&run=2026-01-31T18:00&models=ecmwf_ifs&hourly=wind_speed_100m&forecast_days=16&wind_speed_unit=ms)
- **[TEST] Time axis.** A Single-Runs response starts at the init time, not at local midnight: `run=2026-01-31T12:00&forecast_days=3` → 72 steps, 2026-01-31T12:00…2026-02-03T11:00. `forecast_hours=N` returns N steps from init. Hours beyond the model horizon come back as `null` (`forecast_days=16` → 384 steps, of which 361 are non-null for 00/12Z) — [test URL](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&run=2026-01-31T12:00&models=ecmwf_ifs&hourly=wind_speed_100m&forecast_days=16&wind_speed_unit=ms)
- **[TEST] Other models before 2026-04-02 fail.** `icon_global`, `ecmwf_ifs025`, `ecmwf_aifs025_single`, `gfs_global`/`ncep_gfs013` and `ncep_gfs025` → 400 "requested model run is not available" for 2026-01-31 and 2026-04-01, and OK for 2026-04-02 (GFS 0.25 was still unavailable for 2025-06…2026-02 runs) — [example](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=icon_global&hourly=wind_speed_10m&run=2026-04-01T00:00)
- Daily aggregations in Single-Runs are unreliable. Maintainer: "Daily aggregations do not work in most cases, because a single run does not provide the full 24 hours of the first day… single runs API has been primarily designed with customers in the energy sector" — [issue #1917](https://github.com/open-meteo/open-meteo/issues/1917)

#### Run-publication latency (needed for as-of cut-offs)
- **[TEST]** From meta.json for the 2026-09-23 00Z run, availability delay on api.open-meteo.com:

  | Model | Delay |
  |---|---|
  | ecmwf_ifs 9 km | 7.0 h |
  | ecmwf_ifs025 | 7.8 h |
  | ecmwf_aifs025_single | 5.7 h |
  | ncep_gfs013 | 5.5 h |
  | ncep_gfs025 | 6.5 h |
  | dwd_icon | 3.7 h |
  | cmc_gem_gdps_15km | 5.9 h |
  | ukmo_global_deterministic_10km | 8.4 h |
  | meteofrance_arpege_world025 | 4.0 h |
  | cma_grapes_global | 6.3 h |
  | jma_gsm (18Z run) | 9.5 h |

  Also: `kma_gdps` last run 2026-03-31 18Z (feed stale). ERA5 `data_end_time` lags about 5–6 days. `ecmwf_ifs_analysis_long_window` lags about 2 days. Single-runs-api meta for ecmwf_ifs showed availability at 06:32Z, compared with 07:00Z on api.open-meteo.com.

  Test URLs: [meta ecmwf_ifs](https://api.open-meteo.com/data/ecmwf_ifs/static/meta.json); [single-runs meta](https://single-runs-api.open-meteo.com/data/ecmwf_ifs/static/meta.json)
- There is no per-historical-run publication timestamp. Maintainer (2026-06-07): "we do store this information in a meta data json, but it's currently not yet exposed. It will be available in the next weeks." — [issue #1889](https://github.com/open-meteo/open-meteo/issues/1889)
- ECMWF open data at full 9 km resolution since 2025-10-01 ("ECMWF transitioned to open-data on 1st October 2025"). The open-data IFS 0.25° has an extra ~2 h delay versus real-time dissemination — [ECMWF API docs](https://open-meteo.com/en/docs/ecmwf-api)

### Inferences
- `_previous_day1` and `_previous_day2` are **not** "forecast issued at time T". Each UTC day's 24 hours come from 4 different runs (00/06/12/18Z), and the later runs were published after any fixed daily issue time. Example: V=D+1 18–23 UTC for `previous_day1` comes from run D 18Z, which is public around D+1 01:00 UTC for ecmwf_ifs. That is later than an issue time of, e.g., D 12:00 local (06:00–07:00 UTC).
  - General rule: `previous_dayN` at valid time V is leakage-free for issue time T only if floor6(V) − 24N h + latency ≤ T.
  - With a latency of ≈7 h, `previous_day2` is safe only for V ≤ ≈T+41…46 h, and `previous_day1` only for V ≤ ≈T+17…22 h.
  - This matters for the 24–48 h target.
- The Single-Runs `ecmwf_ifs` archive gives true as-issued 9 km runs covering the whole test month (Feb 2026) and training from 2024-03-14. Caveat: 2024-03-14…2024-11-11 are 49r1 hindcasts with 00/12Z runs only and a 10-day horizon, not the operational cycle 48r1 that was live then. The model version changes at 49r1 (2024-11-12) and at 50R1 (2026-05-12 06Z). The test month (Feb 2026) is pure 49r1 operational.
- For 2023-03-11 … 2024-02 (start of the SCADA training window), Open-Meteo has no forecast-lead-24–48 h data for the relevant models except:
  - JMA GSM `previous_dayN`: 0.5°, 6-hourly, 10 m wind only
  - GFS T2m `previous_dayN`
  
  Only Historical-Forecast (lead 0–5 h) and ERA5/IFS analysis cover that period.
- Historical-Forecast and ERA5/`archive` must never be used as test-period inputs, because they are analysis-like and would leak. For training they introduce train/serve skew (#1747).

### Gaps
- Official docs give no formal definition for 1-hourly or 12-hourly models. By analogy, HRRR `previous_day1` would be exact +24 h, and 12-hourly GEM Global would be +24…35 h; not verified.
- Whether per-run publication timestamps are now exposed (promised June 2026 in #1889) was not verified. meta.json only shows the latest run.
- The Single-Runs table says "IFS HRES… 10 days", but 00/12Z runs since 2024-11-12 return 360 h (15 days) of non-null data. The docs table appears stale.

---

## Q2. Models available, coverage of Central Asia / Kazakhstan, resolution, best_match behaviour at the site

### Takeaway
Only global models cover Shelek/Almaty. No Open-Meteo regional (≤7 km) model covers Kazakhstan; JMA MSM and KMA LDPS cover only Japan/Korea.

At this site, `best_match` uses **ECMWF IFS HRES 9 km** for surface and 10–200 m wind. It fills IFS-missing variables (`temperature_80m`, pressure levels) from ICON, and it also depends on GFS 0.25 (which is why `best_match` single runs fail before 2026-04-02).

Usable archived-forecast models for Feb 2026:
- ecmwf_ifs (single + previous)
- ecmwf_ifs025, gfs_global/seamless, icon_global/seamless, ecmwf_aifs025_single, gem_global (previous only)
- ukmo/jma/kma (10 m wind only)

### Cited Findings
- Model IDs exposed in the Forecast/Previous/Historical-Forecast pickers:
  - ECMWF: `best_match`, `ecmwf_ifs` (IFS HRES 9 km), `ecmwf_ifs025`, `ecmwf_aifs025_single`
  - CMA/BOM: `cma_grapes_global`, `bom_access_global`
  - NCEP: `ncep_gfs_seamless`, `ncep_gfs_global` ("GFS Global 0.11°/0.25°"), `ncep_hrrr_conus`, `ncep_nbm_conus`, `ncep_nam_conus`, `ncep_aigfs025`, `ncep_hgefs025_ensemble_mean`
  - JMA: `jma_seamless`, `jma_msm`, `jma_gsm`
  - KMA: `kma_seamless`, `kma_ldps`, `kma_gdps`
  - DWD: `dwd_icon_seamless`, `dwd_icon_global`, `dwd_icon_eu`, `dwd_icon_d2`
  - GEM: `cmc_gem_seamless`, `cmc_gem_gdps`, `cmc_gem_rdps`, `cmc_gem_hrdps`, `cmc_gem_hrdps_west`
  - Météo-France: `meteofrance_seamless`, `meteofrance_arpege_world`, `meteofrance_arpege_europe`, `meteofrance_arome_france`, `meteofrance_arome_france_hd`
  - UKMO: `ukmo_seamless`, `ukmo_global_deterministic_10km`, `ukmo_uk_deterministic_2km`
  - Others: `italia_meteo_arpae_icon_2i`, `metno_*`, `knmi_*`, `dmi_*`, `meteoswiss_icon_*`, `geosphere_*`, `chmi_aladin_*`
  
  Short aliases such as `gfs_global`, `icon_global`, `gem_global`, `gfs_seamless`, `icon_seamless` are also accepted, as the tests show. Source: [docs options.ts](https://github.com/open-meteo/open-meteo-website/blob/main/src/routes/en/docs/options.ts)
- Global model specs:
  - ECMWF IFS HRES 9 km (O1280): 1-hourly to 90 h, 3-hourly to 144 h, 6-hourly after; 15 days; every 6 h
  - IFS 0.25 open-data: 3-hourly (6-hourly after 144 h)
  - AIFS Single 0.25°: 6-hourly
  - Open-Meteo "dynamically interpolates all data to a consistent 1-hourly time-series"
  
  Source: [ECMWF API docs](https://open-meteo.com/en/docs/ecmwf-api)
- AWS open-data model table (resolution / time step / forecast length / updates / archive since):

  | Model | Resolution | Time step | Forecast length | Updates | Archive since |
  |---|---|---|---|---|---|
  | dwd_icon | 0.1° | hourly | 7.5 d | 6-hourly | 2023-12-15 |
  | ncep_gfs013 | 0.11° | hourly | 16 d | — | 2023-12-15 |
  | ncep_gfs025 | 0.25° | — | — | — | — (38 pressure levels) |
  | ecmwf_ifs025 | — | 3-hourly | — | — | 2024-02-03 |
  | ecmwf_aifs025_single | — | 6-hourly | — | — | 2025-02-20 |
  | ukmo_global_deterministic_10km | 0.09° | hourly | 7 d | — | 2022-03-01 |
  | cmc_gem_gdps | 0.15° | 3-hourly | 10 d | 12-hourly | — |
  | jma_gsm | 0.5° | 6-hourly | 11 d | — | — |
  | cma_grapes_global | 0.125° | 3-hourly | — | — | 2024-01-01 |
  | bom_access_global | ~15 km | hourly | — | — | — |
  | kma_gdps | 0.13° | 3-hourly | 12 d | — | 2024-07-01 |
  | meteofrance_arpege_world025 | 0.25° | — | 4 d | — | — |

  Source: [open-meteo/open-data README](https://github.com/open-meteo/open-data)
- Stale feeds. Maintainer (2026-06-05): "for `bom_access_global` there is no data available for almost 12 months now". Also, "`cmc_gem_rdps`… was just recently replaced by `cmc_gem_rdps_10km`" — [issue #1891](https://github.com/open-meteo/open-meteo/issues/1891). **[TEST]** `kma_gdps` meta.json last run 2026-03-31 18Z — [meta](https://api.open-meteo.com/data/kma_gdps/static/meta.json)
- Best-match semantics: "The default Best Match provides the best forecast for any given location worldwide. Seamless combines all models from a given provider into a seamless prediction." IFS HRES "is the default global model in the generic weather forecast API if no higher resolution weather models are available" — [Previous Runs docs](https://open-meteo.com/en/docs/previous-runs-api); [ECMWF API docs](https://open-meteo.com/en/docs/ecmwf-api)
- **[TEST] best_match at the site (Forecast API, 2026-09-23):**
  - `best_match` = `ecmwf_ifs` (same cell 43.620384, 78.47891) for wind at 10/80/100/120 m, T2m, surface_pressure, boundary_layer_height and CAPE
  - `temperature_80m` and `wind_speed_850hPa` in best_match equal the `icon_seamless` values (IFS 9 km lacks them)
  - Previous-Runs `best_match` `wind_speed_100m_previous_day1/2` = `ecmwf_ifs`
  
  Test URLs: [forecast compare](https://api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=best_match,ecmwf_ifs,icon_seamless,gfs_seamless,ecmwf_ifs025&hourly=wind_speed_100m,temperature_80m,wind_speed_850hPa&forecast_hours=4&wind_speed_unit=ms); [prev-runs best_match](https://previous-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=best_match&hourly=wind_speed_100m,wind_speed_100m_previous_day1,wind_speed_100m_previous_day2&start_date=2026-02-01&end_date=2026-02-02&wind_speed_unit=ms)
- **[TEST]** Single-Runs with no `models` (best_match), `run=2026-01-31T12:00` → 400 "The requested model run is not available. Model: ncep_gfs025". So best_match composes GFS 0.25 as well, and one missing component run fails the whole request — [test URL](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&run=2026-01-31T12:00&hourly=wind_speed_100m). The maintainer confirms this is intentional for seamless domains and recommends addressing individual models — [issue #1891](https://github.com/open-meteo/open-meteo/issues/1891)
- **[TEST] Grid cells and Previous-Runs wind availability at the site, Feb 2026:**

  | model | returned cell | wind vars with `previous_day1` data (Feb 2026) | `previous_day1` start at site |
  |---|---|---|---|
  | ecmwf_ifs (9 km) | 43.620384, 78.47891 | 10, 80, 100 (and 120/180/200) m | **2025-10-01T00** (none in 2023–2024) |
  | ecmwf_ifs025 | 43.75, 78.5 | 10, 100 m (80 m null) | 2024-03-06T18 (17406/17424 h non-null to 2026-03-01) |
  | gfs_global (= gfs_seamless here) | 43.638138, 78.515625 | 10, 80, 100 m | 100 m: 2024-02-16T06; 10 m: 2024-01-19T12; T2m: 2021-03-24 |
  | icon_global (= icon_seamless here) | 43.625, 78.5 | 10, 80, 100 m | 80 m: 2024-02-16T12 (17868/17880) |
  | ecmwf_aifs025_single | 43.75, 78.5 | 10, 100 m | 2025-02-18T00 (no gaps) |
  | gem_global | 43.65, 78.60 | 10, 80 m (100 m null) | 80 m: 2024-02-16T12 |
  | ukmo_global_deterministic_10km | 43.6875, 78.46875 | 10 m only | — |
  | jma_gsm | 43.5, 78.5 | 10 m only | 2017-01-01 (docs say 2018) |
  | kma_gdps | 43.64, 78.54 | 10 m only | — |
  | meteofrance_arpege_world, cma_grapes_global, bom_access_global | — | `previous_dayN` all null in Feb 2026 (day0 present for ARPEGE/CMA) | — |

  Test URLs: [sweep pattern](https://previous-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=ecmwf_ifs025&hourly=wind_speed_100m,wind_speed_100m_previous_day1,wind_speed_100m_previous_day2,wind_speed_80m_previous_day1,wind_speed_10m_previous_day1&start_date=2026-02-01&end_date=2026-02-02&wind_speed_unit=ms); [coverage ecmwf_ifs 2025](https://previous-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=ecmwf_ifs&hourly=wind_speed_100m_previous_day1&start_date=2025-01-01&end_date=2025-12-31)
- Ensembles:
  - Ensemble API models: ECMWF IFS 0.25° ENS (51 members, 3-hourly, 15 d), AIFS ENS, GFS Ensemble 0.25° (31 members, 10 d) and 0.5° (35 d), ICON-EPS (40 members, 26 km, 7.5 d), GEM (21), BOM ACCESS-GE, MOGREPS-G (18), Google WeatherNext 2 (64 members). Native 9 km IFS ENS is Europe only — [Ensemble docs](https://open-meteo.com/en/docs/ensemble-api)
  - **[TEST]** Ensemble API `start_date=2026-02-01` → 400 "Parameter 'start_date' is out of allowed range from 2026-06-22 to 2026-10-28", for members and for `ecmwf_ifs025_ensemble_mean` alike. There is no ensemble archive for Feb 2026 on the free API — [test URL](https://ensemble-api.open-meteo.com/v1/ensemble?latitude=43.64515&longitude=78.535604&models=ecmwf_ifs025&hourly=wind_speed_100m&start_date=2026-02-01&end_date=2026-02-01)
  - Previous-Runs lists "NCEP HGEFS Mean", but **[TEST]** `ncep_hgefs025_ensemble_mean` `previous_day1` for 2026-02-01 was all null — [test URL](https://previous-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=ncep_hgefs025_ensemble_mean&hourly=wind_speed_10m_previous_day1&start_date=2026-02-01&end_date=2026-02-01)

### Inferences
- For the 2 turbines, every model resolves both coordinates to the same grid cell (ECMWF 9 km cell ≈5 km away). Point NWP gives identical inputs for both turbines, so turbine differences must come from SCADA-side modelling. Querying neighbouring cells (e.g., a small lat/lon grid via multi-location calls) is the only way to get spatial context.
- Multi-model features for the full test month: `ecmwf_ifs` from Single-Runs (true runs), plus `previous_dayN` from gfs/icon/ecmwf_ifs025/aifs/gem, subject to the lead-time mixing caveat in Q1.
- Best practice is to always pass explicit `models=` (e.g., `ecmwf_ifs`), never `best_match`/seamless, in archive requests. That keeps results reproducible and avoids failures when a component run is missing.

### Gaps
- Open-Meteo does not document the exact best_match blending rules per region or variable. The composition above is inferred from value matching.
- I did not test UKMO / ARPEGE / CMA Historical-Forecast at the site, nor whether ARPEGE/CMA `previous_dayN` exist in other months.

---

## Q3. Wind-power-relevant hourly variables, per-model availability, units, 15-minutely data, timezone behaviour (incl. KZ 2024 change)

### Takeaway
- **ECMWF IFS 9 km** gives natively 10/100/200 m wind, gusts, BLH, CAPE, MSLP (surface pressure derived), T2m/dewpoint. It has no pressure levels and no `temperature_80m+`. The API still returns 80/120/180 m wind for it, presumably interpolated.
- **ICON** has native 80/180 m wind and temperature plus pressure levels.
- **GFS** has 80/100 m plus pressure levels (0.25°).
- **IFS 0.25** has 10/100 m plus 9 pressure levels.
- 15-minutely data is only interpolated for Kazakhstan.
- `timezone=Asia/Almaty` applies today's offset (+5) to the whole series, even for 2023 when Almaty was +6. Use `timezone=GMT` (or fixed `Etc/GMT-6`).

### Cited Findings
- Hourly variables (Forecast API; the archive endpoints use identical names):
  - surface: `temperature_2m`, `relative_humidity_2m`, `dew_point_2m`, `pressure_msl`, `surface_pressure`, `cloud_cover*`
  - wind: `wind_speed_10m/80m/120m/180m`, `wind_direction_*`, `wind_gusts_10m` ("maximum of the preceding hour"), `temperature_80m/120m/180m`
  - additional: `cape`, `lifted_index`, `convective_inhibition`, `freezing_level_height`, `boundary_layer_height`, `total_column_integrated_water_vapour`, `is_day`
  - pressure levels: `wind_speed_<L>hPa`, `wind_direction_<L>hPa`, `temperature_<L>hPa`, `relative_humidity_<L>hPa`, `geopotential_height_<L>hPa`, `vertical_velocity_<L>hPa`, `dew_point_<L>hPa`
  - `wind_speed_100m/200m` exist too (ECMWF/Previous-Runs lists)
  
  "Most weather variables are given as an instantaneous value for the indicated hour." Sources: [Forecast docs](https://open-meteo.com/en/docs); [options.ts](https://github.com/open-meteo/open-meteo-website/blob/main/src/routes/en/docs/options.ts); [ECMWF options.ts](https://github.com/open-meteo/open-meteo-website/blob/main/src/routes/en/docs/ecmwf-api/options.ts)
- Pressure levels: "1000 hPa is roughly between 60 and 160 meters above sea level… Altitudes are in meters above sea level (not above ground)". Single-Runs picker levels: 1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50. At the 555 m-elevation site (surface pressure ≈950 hPa in the tests), 1000 hPa is below ground, so the relevant levels are 925/850 — [Forecast docs](https://open-meteo.com/en/docs); [single-runs options.ts](https://github.com/open-meteo/open-meteo-website/blob/main/src/routes/en/docs/single-runs-api/options.ts)
- ECMWF native fields:
  - "U and V wind components — 10 m, 100 m, pressure levels"
  - "The IFS HRES 9 km model additionally provides native dew point, direct radiation, visibility, showers and boundary layer height, but no pressure-level fields. Pressure-level data is available only from the 0.25° open-data models."
  - "Surface pressure — Calculated from mean sea-level pressure, 2 m temperature and terrain elevation."
  
  Source: [ECMWF API docs](https://open-meteo.com/en/docs/ecmwf-api)
- The S3 archive for `ecmwf_ifs` stores `wind_u/v_component_10m/100m/200m`, `wind_gusts_10m`, `boundary_layer_height`, `cape`, `convective_inhibition`, `pressure_msl`, `roughness_length`, etc. There is no 80/120/180 m wind and no `temperature_80m`. `dwd_icon` stores `wind_u/v_component_80m/180m`, `temperature_80m/180m` and 850 hPa fields. `ecmwf_ifs025` stores 100 m wind and 850 hPa fields — [S3 listing data/ecmwf_ifs/](https://openmeteo.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=data/ecmwf_ifs/); [S3 explorer](https://openmeteo.s3.amazonaws.com/index.html#data/)
- **[TEST]** `ecmwf_ifs` single run 2026-01-31T12Z at the site:
  - non-null: `wind_speed_10/80/100/120/180/200m`, `wind_direction_100m`, `wind_gusts_10m`, `temperature_2m`, `surface_pressure` (~953.6 hPa), `pressure_msl`, `relative_humidity_2m`, `boundary_layer_height`, `cape`
  - all null with unit "undefined": `temperature_80m`, `wind_speed_850hPa`, `wind_speed_925hPa`
  - sample at 2026-02-01T00Z: 80 m 1.67, 100 m 1.72, 120 m 1.75, 180 m 2.28, 200 m 2.30 m/s (monotone, consistent with interpolation between native 10/100/200 m)
  
  Source: [test URL](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&run=2026-01-31T12:00&models=ecmwf_ifs&hourly=wind_speed_10m,wind_speed_80m,wind_speed_100m,wind_speed_120m,wind_speed_180m,wind_speed_200m,wind_direction_100m,wind_gusts_10m,temperature_2m,temperature_80m,surface_pressure,pressure_msl,relative_humidity_2m,boundary_layer_height,cape,wind_speed_850hPa,wind_speed_925hPa&wind_speed_unit=ms&forecast_days=3)
- **[TEST]** In the Forecast API at the site:
  - `gfs_seamless` returns 10/80/100/120 m wind, `temperature_80m`, 850 hPa and BLH
  - `ecmwf_ifs025` returns 10/100 m and 850 hPa (no 80/120 m, no BLH)
  - `icon_seamless` returns 10/80/100/120 m, `temperature_80m` and 850 hPa (no BLH)
  
  Source: [test URL](https://api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=gfs_seamless,ecmwf_ifs025,icon_seamless&hourly=wind_speed_10m,wind_speed_80m,wind_speed_100m,wind_speed_120m,temperature_80m,wind_speed_850hPa,boundary_layer_height&forecast_hours=4&wind_speed_unit=ms)
- Units and time format:
  - `wind_speed_unit` = `kmh` (default) | `ms` | `mph` | `kn`
  - `temperature_unit` = celsius | fahrenheit
  - `precipitation_unit` = mm | inch
  - `timeformat` = `iso8601` | `unixtime` ("all timestamp are in GMT+0")
  - `format` = json (default) | csv | xlsx (flatbuffers via the SDK)
  - Pressures in hPa; BLH in m; CAPE in J/kg
  
  Source: [Forecast docs](https://open-meteo.com/en/docs); [Previous Runs docs](https://open-meteo.com/en/docs/previous-runs-api)
- Grid-cell selection and downscaling:
  - `cell_selection` = `land` (default: "a suitable grid-cell on land with similar elevation… using a 90-meter digital elevation model") | `sea` | `nearest`
  - `elevation=` sets the elevation for statistical downscaling; `elevation=nan` disables it
  - the response `latitude`/`longitude` are "the center of the weather grid-cell… might be a few kilometres away"
  
  **[TEST]** With `cell_selection=nearest&elevation=nan` the same ECMWF cell was returned, with elevation 638 m (grid-cell mean) instead of the 555 m DEM value, and the wind values were unchanged. Sources: [Forecast docs](https://open-meteo.com/en/docs); [test URL](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&run=2026-01-31T00:00&models=ecmwf_ifs&hourly=wind_speed_100m,temperature_2m&wind_speed_unit=ms&forecast_hours=3&cell_selection=nearest&elevation=nan)
- 15-minutely: `minutely_15=` data "is based on NOAA HRRR model for North America and DWD ICON-D2 and Météo-France AROME model for Central Europe… other weather variables… will use interpolation". Wind at 15 min: `wind_speed_10m/80m`, `wind_gusts_10m`. Single-Runs and Historical-Forecast say the same ("Only available in Central Europe and North America. Other regions use interpolated hourly data") — [Forecast docs](https://open-meteo.com/en/docs); [Single Runs docs](https://open-meteo.com/en/docs/single-runs-api)
- Backward-aggregated variables (`wind_gusts_10m`, precipitation, radiation) are null at the init hour of a run: "They are not available for the initialization hour of a model run (from the upstream provider). This is expected" — [issue #1905](https://github.com/open-meteo/open-meteo/issues/1905). **[TEST]** `wind_gusts_10m` non-null only for lead 1…360 h — [test URL](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=ecmwf_ifs&hourly=wind_gusts_10m&run=2026-01-31T00:00&forecast_days=16)
- Timezone parameter: `timezone` default GMT; any IANA name or `auto`; "For multiple coordinates, a comma separated list of timezones". Response includes `utc_offset_seconds` and `timezone_abbreviation` — [Forecast docs](https://open-meteo.com/en/docs)
- Maintainer: "The API operates solely in the 'current' timezone, with no DST adjustments applied throughout the time series. For processing long time-series data, we recommend using GMT+0" (2025-02-28) — [issue #1255](https://github.com/open-meteo/open-meteo/issues/1255); related open issue [#488](https://github.com/open-meteo/open-meteo/issues/488)
- **[TEST]** Timezone behaviour:
  - `timezone=Asia/Almaty` → `utc_offset_seconds=18000`, abbreviation GMT+5, for 2026-02-01, for 2023-03-11 and across 2024-02-29..03-01
  - `Europe/Berlin` for 2024-01-10 → +7200 (the current CEST offset, although January is CET +1)
  - `timezone=Etc/GMT-6` → fixed +21600 (GMT+6)
  
  Test URLs: [Almaty 2023](https://archive-api.open-meteo.com/v1/archive?latitude=43.64515&longitude=78.535604&hourly=wind_speed_100m&start_date=2023-03-11&end_date=2023-03-11&timezone=Asia/Almaty); [Berlin Jan 2024](https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&hourly=temperature_2m&start_date=2024-01-10&end_date=2024-01-10&timezone=Europe/Berlin); [Etc/GMT-6](https://archive-api.open-meteo.com/v1/archive?latitude=43.64515&longitude=78.535604&hourly=wind_speed_100m&start_date=2023-03-11&end_date=2023-03-11&timezone=Etc/GMT-6)
- Kazakhstan switched to a single UTC+05:00 zone on 2024-03-01. Almaty and the eastern regions moved clocks back one hour (from UTC+6), and IANA `Asia/Almaty` was updated accordingly — [Wikipedia: Time in Kazakhstan](https://en.wikipedia.org/wiki/Time_in_Kazakhstan); [Astana Times](https://astanatimes.com/2024/01/kazakhstan-switches-to-utc05-00-time-zone-from-march-1/); [timeanddate](https://www.timeanddate.com/news/time/kazakhstan-single-time-zone.html)

### Inferences
- The SCADA data is in fixed UTC+6. Request all Open-Meteo data with `timezone=GMT` (or `timeformat=unixtime`) and shift by +6 h yourself, or request `timezone=Etc/GMT-6`. `Asia/Almaty` would silently mis-align all pre-2024-03-01 data by 1 h, and would mis-align all data by 1 h relative to a fixed UTC+6 SCADA clock.
- For hub-height features (hub height unknown here; typically 80–120 m), each model contributes different heights:
  - `ecmwf_ifs`: `wind_speed_100m` (native), `wind_speed_200m`/`wind_speed_10m` for shear, BLH, gusts, `surface_pressure` + `temperature_2m` for air density
  - ICON/GFS: native 80 m, `temperature_80m`, 850/925 hPa wind for stability or low-level-jet context
- IFS 0.25 (3-hourly) and AIFS (6-hourly) hourly values are temporal interpolations. Hourly variability in those features is synthetic.

### Gaps
- Open-Meteo does not document the interpolation or extrapolation method it uses for 80/120/180 m wind from ECMWF's native 10/100/200 m. It is inferred (not confirmed) from the absence of native fields.
- Which pressure levels exist for each global model in Previous-Runs is moot, because `_previous_dayN` is rejected for pressure-level variables. For Feb 2026, pressure-level winds as-issued are only available from Single-Runs, and only for models archived from 2026-04-02, i.e. not for the test month.

---

## Q4. Rate limits, terms, licence/attribution, multi-location calls, request weighting, typical failure modes

### Takeaway
- **Free tier, non-commercial, no API key:** <600 calls/min, <5,000/hour, <10,000/day, 300,000/month.
- **Heavy calls count as several calls:** a call counts extra for more than 10 variables or more than 2 weeks of data, and each location counts separately.
- **Concurrency:** one concurrent request per IP; a queue of more than 5 gives HTTP 429.
- **Licence:** data is CC BY 4.0 with attribution and a link; the server code is AGPLv3.
- **Paid tiers:** `customer-*` hosts with `&apikey=`. Historical/Previous/Single-Runs require the Professional plan or higher.

### Cited Findings
- Terms, non-commercial use: "Less than 10'000 API calls per day, 5'000 per hour and 600 per minute. You may only use the free API services for non-commercial purposes. You accept to the CC-BY 4.0 licence… We reserve the right to block applications and IP addresses that misuse our service."
  - Non-commercial examples: "public research conducted at public institutions", "educational content"
  - Commercial examples: "Conducting undisclosed research at commercial entities", apps with subscriptions or ads
  - Governing law: Switzerland; operator OpenMeteo GmbH
  
  Source: [Terms](https://open-meteo.com/en/terms)
- Plan table:

  | Plan | Commercial use | Rate limits | Monthly calls |
  |---|---|---|---|
  | Free | no | 600/min, 5,000/h, 10,000/day | 300,000/month |
  | Standard | yes | unlimited per min/h/day | 1M/month |
  | Professional | yes | unlimited per min/h/day | 5M/month |
  | Enterprise | yes | unlimited per min/h/day | >50M/month |

  - The customer endpoint is `customer-api.open-meteo.com` with `&apikey=…`
  - "Historical, climate, ensemble, and satellite radiation APIs require the Professional API Plan or higher"; the table row covering Historical Forecast / Previous Model Runs / Single Runs shows Free ✅, Standard ❌, Professional ✅, Enterprise ✅
  - Monthly limits are not hard-enforced yet (email alerts at 80/90/100 %)
  - Paid plans target 99.9 % uptime; status page: status.open-meteo.com
  
  Source: [Pricing](https://open-meteo.com/en/pricing)
- Call weighting: "Requests for data covering more than 10 weather variables or extending over a period of more than 2 weeks for a single location are considered multiple API calls… 2 weeks of data with 15 weather variables will be calculated as 1.5 API calls, while 4 weeks of data equals 3.0 API calls" — [Pricing FAQ](https://open-meteo.com/en/pricing). The maintainer (2023) adds that multiple locations are weighted per location ("2 locations in one call, the weight is adjusted to 2 calls"), and that archive factors were later relaxed for long ranges — [issue #438](https://github.com/open-meteo/open-meteo/issues/438)
- Concurrency limit: "the free API is limited to 1 concurrent request per IP address. Consecutive requests will be queued. If more than 5 requests are queued, you get the error 'Too many concurrent requests'… in place since March 2025" — [issue #1650](https://github.com/open-meteo/open-meteo/issues/1650); [ConcurrencyGroupLimiter.swift](https://github.com/open-meteo/open-meteo/blob/main/Sources/App/Helper/Vapor/ConcurrencyGroupLimiter.swift)
- Rate-limit errors come back as HTTP 429 with reasons such as "Minutely API request limit exceeded" / "Daily API request limit exceeded"; the JSON distinguishes concurrency, minute, hourly and daily limits — [issue #438](https://github.com/open-meteo/open-meteo/issues/438); [issue #439](https://github.com/open-meteo/open-meteo/issues/439); [issue #1650](https://github.com/open-meteo/open-meteo/issues/1650)
- Licence and attribution:
  - "API data are offered under Attribution 4.0 International (CC BY 4.0)… You must include a link next to any location Open-Meteo data are displayed"
  - Code is AGPLv3
  - Citation: Zippenfenig, P. (2023). Open-Meteo.com Weather API. Zenodo. doi:10.5281/ZENODO.7970649
  - Upstream data credited: DWD, ECMWF, NOAA NCEP, CMC, Météo-France, JMA, MET Norway, CMA, BOM, KNMI, DMI, UK Met Office, ItaliaMeteo-ARPAE, MeteoSwiss, Copernicus C3S (ERA5)
  
  Source: [Licence](https://open-meteo.com/en/licence)
- Multi-location calls: "Multiple coordinates can be comma separated. E.g. `&latitude=52.52,48.85&longitude=13.41,2.35`… the JSON output changes to a list of structures. CSV and XLSX formats add a column `location_id`". Elevation and timezone can also be comma-separated — [Forecast docs](https://open-meteo.com/en/docs). **[TEST]** Two turbines in one Single-Runs call returned a 2-element list, both with cell 43.620384, 78.47891 and identical values — [test URL](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.645150,43.643198&longitude=78.535604,78.538828&run=2026-01-31T00:00&models=ecmwf_ifs&hourly=wind_speed_100m&wind_speed_unit=ms&forecast_hours=6)
- Errors: "a JSON error object is returned with a HTTP 400 status code" — [Forecast docs](https://open-meteo.com/en/docs)

#### Failure modes observed / reported
- Single-Runs, run not archived → 400 `{"error":true,"reason":"The requested model run is not available. Model: X, run: …Z"}` (**[TEST]**, above).
- Seamless/best_match with one missing component → whole request fails. Sometimes the response is HTTP **200 with a plain-text body** "Unexpected error while streaming data: modelRunUnavailable(...)". The maintainer says the JSON/400 fix is "not trivial" — [issue #1891](https://github.com/open-meteo/open-meteo/issues/1891)
- Unsupported variable for a model → HTTP 200 with an all-null array and unit `"undefined"`. **[TEST]** `models=gfs025&hourly=wind_speed_10m` gives an all-null array and looks like success — [test URL](https://single-runs-api.open-meteo.com/v1/forecast?latitude=43.64515&longitude=78.535604&models=gfs025&hourly=wind_speed_10m&run=2026-01-31T00:00&forecast_hours=2)
- Trailing nulls in Single-Runs, beyond the valid horizon and in some cases a bug: "23 trailing null values… most likely is an issue somewhere in our code" (June 2026, open) — [issue #1905](https://github.com/open-meteo/open-meteo/issues/1905)
- Outages:
  - Previous-Runs HTTP 500 (Mar 2026) — [#1774](https://github.com/open-meteo/open-meteo/issues/1774)
  - archive-api ConnectTimeout (May 2026) — [#1864](https://github.com/open-meteo/open-meteo/issues/1864)
  - "single runs down" (June 2026) — [#1909](https://github.com/open-meteo/open-meteo/issues/1909)
  - customer archive 403 (Apr 2026) — [#1812](https://github.com/open-meteo/open-meteo/issues/1812)
  - **[TEST]** `ensemble-api.open-meteo.com/data/ecmwf_ifs/static/meta.json` → 500 (not a valid ensemble domain)
- Eventual consistency across redundant servers: wait 10 min after `last_run_availability_time` — [Model updates](https://open-meteo.com/en/docs/model-updates)

### Inferences
- A backtest pull is small even under weighted counting:
  - 29 daily as-of issues × 1–4 runs × 1 call (≤10 variables, ≤16 days → about 1–2 weighted calls each) × a few models
  - Training pulls: ecmwf_ifs single runs 2024-03-14→2026-01-31 is about 690 days × 2–4 runs ≈ 1.4k–2.8k calls per variable set
  
  That fits the free daily or monthly limits if spread over a day or two, with sequential requests (1 concurrent/IP).
- Because the tool fails silently (200 + nulls / "undefined" unit, or 200 + text body), the pipeline must validate the unit field, the non-null fraction and the JSON parse, not only the HTTP status.
- Whether a hackathon (evaluators rerunning without keys) counts as "non-commercial" depends on the organiser. If a company sponsors it, "undisclosed research at commercial entities" could arguably count as commercial. This is a legal grey zone to flag, not resolve.

### Gaps
- Response headers (e.g., any `X-RateLimit-*`) were not inspected. I found no documented header-based quota info.
- The exact current weighting rules for archive/single-runs endpoints (after the 2023 adjustment) are not published beyond the Pricing FAQ.

---

## Q5. Official Python client, FlatBuffers SDK, caching/retry, self-hosting (Docker) and the AWS S3 open-data archive (.om files)

### Takeaway
- `openmeteo-requests` (v1.7.5) fetches FlatBuffers responses via `niquests`/`requests` into numpy/pandas/polars. It works with any endpoint URL, so it also works for Single-Runs, Previous-Runs and archive calls.
- `requests-cache` + `retry-requests` is the officially recommended pattern for caching and retries.
- Bulk data is on `s3://openmeteo` (us-west-2) as `.om` files. The run-based layout (`data_run/`) is kept only for about 3 months, so the Feb 2026 runs are not on S3 any more. The rolling `data/` layout is essentially the Historical-Forecast series.
- Previous-Runs data does not appear in the bucket.

### Cited Findings
- Client README:
  - "based on the Python library `niquests` and compatible with the `requests` library… use of FlatBuffers instead of JSON… Zero-Copy… numpy, pandas, or polars"
  - usage: `openmeteo = openmeteo_requests.Client(); responses = openmeteo.weather_api(url, params=params)`
  - response accessors: `response.Latitude()`, `Elevation()`, `UtcOffsetSeconds()`, `Model()`; `hourly = response.Hourly()`; `hourly.Time()/TimeEnd()/Interval()` (unix seconds, UTC); `hourly.Variables(i).ValuesAsNumpy()`
  - "The order of variables in hourly or daily is important"
  - `AsyncClient` also exists
  - multiple locations/models return a list of responses
  - caching: `requests_cache.CachedSession('.cache', expire_after=3600)` (or `-1` for indefinite), wrapped in `retry(cache_session, retries=5, backoff_factor=0.2)`
  
  Source: [open-meteo/python-requests README](https://github.com/open-meteo/python-requests)
- Versions (PyPI, checked 2026-09-23):
  - `openmeteo-requests` 1.7.5 (2026-01-19; Python ≥3.9; deps `niquests>=3.15.2`, `openmeteo-sdk>=1.22.0`)
  - `openmeteo-sdk` 1.28.0 (2026-07-29; `flatbuffers==25.9.23`)
  - `omfiles` 1.2.0 (2026-04-23; Python ≥3.10; optional xarray/zarr/fsspec/s3fs)
  - `requests-cache` 1.3.3
  - `retry-requests` 2.0.0 (2023)
  
  Sources: [PyPI openmeteo-requests](https://pypi.org/project/openmeteo-requests/); [PyPI openmeteo-sdk](https://pypi.org/project/openmeteo-sdk/); [PyPI omfiles](https://pypi.org/project/omfiles/); [SDK schemas](https://github.com/open-meteo/sdk)
- S3 open data: "AWS Bucket Name and Region: s3://openmeteo; us-west-2" (AWS Open Data Sponsorship). There are three layouts:
  - `data/<model>/<variable>/<time-chunk>.om`: rolling time series, "multiple years… preserved indefinitely"; this powers the API
  - `data_spatial/<model>/<run>/<timestamp>.om`: retained 7 days
  - `data_run/<model>/<YYYY/MM/DD/hhmmZ>/<variable>.om`: "Data is publicly available on AWS for 3 months, with extended archives available directly from Open-Meteo"; "only 13 pressure levels and model levels below 200 meters are included. At most, one model run every 3 hours is retained"; native model time steps (not interpolated); backward-aggregated variables lack the first step
  
  "Climate, flood, satellite and ensemble models are not published on AWS." Source: [open-meteo/open-data README](https://github.com/open-meteo/open-data); [AWS Registry](https://registry.opendata.aws/open-meteo/)
- **[TEST]** S3 listing on 2026-09-23:
  - top level: `data/`, `data_run/`, `data_spatial/`
  - `data_run/` has 60 model directories, including `ecmwf_ifs`, `ecmwf_ifs025`, `ecmwf_aifs025_single`, `ncep_gfs013`, `ncep_gfs025`, `dwd_icon`, `cma_grapes_global`, `cmc_gem_gdps_15km`, `jma_gsm`, `ukmo_global_deterministic_10km`
  - `data_run/ecmwf_ifs/2026/` contains only months 06–09, and the earliest run directory is `2026/06/20/1800Z/` (one `.om` per variable, ~20–800 MB each, global)
  - `ncep_gfs013`, `dwd_icon` and `ecmwf_aifs025_single` also start at 2026/06
  - no `*_previous_day*` directories under `data/ecmwf_ifs/`
  - `data/ecmwf_ifs/wind_u_component_100m/` holds `year_2018.om`…`year_2022.om` (~33 GB each) plus `chunk_*.om`
  
  Test URLs: [S3 listing data_run/ecmwf_ifs/2026/](https://openmeteo.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=data_run/ecmwf_ifs/2026/); [S3 explorer](https://openmeteo.s3.amazonaws.com/index.html#data/)
- The `data_run/<model>/latest.json` and `data/<model>/static/meta.json` files let you watch run completion (the S3 bucket timestamps were suggested in [issue #1520](https://github.com/open-meteo/open-meteo/issues/1520)). The OM format (C library) has readers for Python (`omfiles`), Rust, Swift and TypeScript — [open-data README](https://github.com/open-meteo/open-data); [om-file-format](https://github.com/open-meteo/om-file-format); [python-omfiles](https://github.com/open-meteo/python-omfiles)
- Self-hosting:
  - `docker pull ghcr.io/open-meteo/open-meteo`
  - `docker run open-meteo sync <model> <vars> --past-days N [--repeat-interval 5]`
  - `docker run -p 8080:8080 open-meteo serve`
  - then `curl "http://127.0.0.1:8080/v1/archive?..."`
  - ERA5-Land T2m for 2 years is ≈8 GB
  - a prebuilt Ubuntu package also exists
  
  Sources: [open-data README](https://github.com/open-meteo/open-data); [open-meteo README](https://github.com/open-meteo/open-meteo). A request to also distribute the S3 data as torrents is open — [issue #1278](https://github.com/open-meteo/open-meteo/issues/1278)

### Inferences
- Evaluators can rerun the pipeline without accounts: `pip install openmeteo-requests requests-cache retry-requests` and the free endpoints need no key. Committing the cached responses (the sqlite cache, or exported parquet of the pulled forecasts) protects reproducibility against archive deletions like the 2026-04 Single-Runs purge, and against rate limits.
- Self-hosting cannot recreate as-issued Feb 2026 multi-model runs. Those runs are gone from `data_run/` on S3, and `sync` only mirrors the rolling series. For the test month, the only as-issued sources remain the hosted Single-Runs (`ecmwf_ifs`) and Previous-Runs APIs.
- For a live pipeline, `data_run/<model>/latest.json` or `meta.json` can be polled to fetch a specific run as soon as it is complete. Alternatively, query the Single-Runs API with `run=` for the latest cycle.

### Gaps
- The client README does not document the query-string parameter the client sets to request FlatBuffers (believed `format=flatbuffers`); not verified. It is also not documented whether the client passes `run=` unchanged to the Single-Runs host. It should, because params are passed through generically, but I did not run Python (not installed on this machine).
- "Extended archives available directly from Open-Meteo" for `data_run` — the terms, prices and whether they cover Jan–Feb 2026 for non-ECMWF models are not published. Given #1969's corruption note, probably not for pre-2026-04-02.

---

## Q6. Known issues / GitHub issues / discussions (2025–2026) about Previous-Runs, Single-Runs, Historical-Forecast gaps, reproducibility, changes

### Takeaway
The archive APIs are young and still changing:
- Single-Runs was launched as a prototype in early 2026, announced 2026-05-15, and had all non-ECMWF runs before 2026-04-02 deleted for corruption.
- Previous-Runs has model-specific gaps (UKMO day1, GFS cloud layers).
- Seamless/best_match requests fail if any component run is missing.
- Reproducibility is at risk because data can be removed or changed. Pin explicit models and cache results.

### Cited Findings
- [#1969](https://github.com/open-meteo/open-meteo/issues/1969) (Jul 2026, closed): Single-Runs cut-off at 2026-04-02 for all models except ECMWF IFS HRES: "Due to data corruption we removed data prior April 2nd… For other local domains it is not possible [to backfill]"; GFS backfill "No ETA".
- [#1747](https://github.com/open-meteo/open-meteo/issues/1747) (Mar–Jun 2026): Historical-Forecast train/serve skew acknowledged. The team: "For most weather agencies it will not be possible to back-fill the single-runs before September 2025."
- [#1750](https://github.com/open-meteo/open-meteo/issues/1750) (Mar 2026): the exact stitching rules for Historical-Forecast and `previous_day1` (see Q1).
- [#2028](https://github.com/open-meteo/open-meteo/issues/2028) (Aug 2026, open): Previous-Runs gaps. Example: UKMO seamless, May 2026, `temperature_2m_previous_day1` missing while day0 and day2 are present.
- [#2132](https://github.com/open-meteo/open-meteo/issues/2132) (Sep 2026, closed): Previous-Runs GFS low/mid/high cloud cover null at day 1–3.
- [#1994](https://github.com/open-meteo/open-meteo/issues/1994) (Jul 2026, closed): GFS precipitation lost ~2/3 of its volume beyond hour 120 (3-hourly PRATE de-averaging bug). This shows that archived values can be affected by processing bugs.
- [#1488](https://github.com/open-meteo/open-meteo/issues/1488) (open): request to add GFS precipitation since 2021 to Previous-Runs.
- [#1891](https://github.com/open-meteo/open-meteo/issues/1891) (Jun 2026, open): Single-Runs fails entirely if any requested/seamless component run is unavailable; 200 OK with a non-JSON body in some cases; BOM without data for ~12 months; `cmc_gem_rdps` replaced by `cmc_gem_rdps_10km`.
- [#1892](https://github.com/open-meteo/open-meteo/issues/1892) (closed Jun 2026): Single-Runs responses do not include the model name when one model is requested.
- [#2020](https://github.com/open-meteo/open-meteo/issues/2020) (Aug 2026, open): Single-Runs error when selecting `cmc_gem_gdps`.
- [#1905](https://github.com/open-meteo/open-meteo/issues/1905) (Jun 2026, open): null values in Single-Runs. Shorter horizons for 06/18Z runs are expected; leading nulls for backward-aggregated variables are expected; some trailing nulls are a bug under investigation. Code reference for per-run horizons: [EcmwfEcpdsDomain.swift](https://github.com/open-meteo/open-meteo/blob/main/Sources/App/EcmwfEcpds/EcmwfEcpdsDomain.swift).
- [#1917](https://github.com/open-meteo/open-meteo/issues/1917) (Jun 2026, closed): daily aggregations and dates wrong for runs not starting at 00:00 local (west of UTC). Fixed in [PR #1936](https://github.com/open-meteo/open-meteo/pull/1936) ("erroneous daily aggregations in single runs api").
- [#1889](https://github.com/open-meteo/open-meteo/issues/1889) (Jun 2026, open): no historical per-run "published at" timestamp yet; promised soon.
- [#1520](https://github.com/open-meteo/open-meteo/issues/1520) (closed Jun 2026): how to know which run the Forecast API served. Answer: use meta.json (`last_run_initialisation_time`, `last_run_availability_time`) or Single-Runs `run=`.
- [#1318](https://github.com/open-meteo/open-meteo/issues/1318) (open since Apr 2025): request to add an hourly "lead time" field to Historical-Forecast. Not implemented.
- [#1374](https://github.com/open-meteo/open-meteo/issues/1374) (Jun 2025) and [#1393](https://github.com/open-meteo/open-meteo/issues/1393) (Jul 2025): pre-Single-Runs era; the maintainer pointed to Previous-Runs ("not exactly the forecast at 6:00, but it represents the day ahead forecast errors quite well"); data "roughly from January 2024". **Outdated context.**
- Blog posts:
  - [Weather forecasts from previous model runs](https://openmeteo.substack.com/p/weather-forecasts-from-previous-model-runs)
  - [Introducing the historical forecast](https://openmeteo.substack.com/p/introducing-the-historical-forecast)
  - [Single Runs API (2026-05-15)](https://openmeteo.substack.com/p/single-runs-api)
- Model changes affecting reproducibility:
  - ECMWF IFS 49r1 hindcasts back the Single-Runs data 2024-03-14…(≈2024-11-11)
  - IFS Cycle 50R1 from 2026-05-12 06 UTC
  - ECMWF open-data at 9 km from 2025-10-01
  
  Sources: [Single Runs docs](https://open-meteo.com/en/docs/single-runs-api); [ECMWF API docs](https://open-meteo.com/en/docs/ecmwf-api)

### Inferences
- The archive can shrink retroactively (the 2026-04 purge) and values can be reprocessed after bug fixes. A backtest that must be rerunnable by evaluators should snapshot the exact responses it used, with request URLs and fetch timestamps, and ship them, rather than rely on re-downloading.
- The ECMWF `ecmwf_ifs` Single-Runs archive has been stable (no deletions reported) and matches the Previous-Runs values exactly for Feb 2026 (**[TEST]** Q1). It is the most trustworthy as-issued source for this project's test window.

### Gaps
- No GitHub Discussions content was reviewed. Unauthenticated GitHub API limits were hit (403) while reading #488/#261.
- I found no reported gaps specific to ECMWF IFS 9 km Single-Runs in Jan–Feb 2026. The spot checks (2026-01-28…02-02 all 4 cycles, 2026-02-15 00Z) were complete, but I did not scan every run of Feb 2026.
