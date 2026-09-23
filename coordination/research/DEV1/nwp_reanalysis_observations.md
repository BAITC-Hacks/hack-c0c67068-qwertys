# Non-Open-Meteo sources: archived NWP forecasts, reanalysis, surface observations, terrain/wind-resource data for the Shelek corridor wind site (43.645N 78.536E, ~555 m)

Research date: 2026-09-23. Many facts below were **verified by live probing** of public buckets/endpoints on 2026-09-23 (anonymous HTTP GET/HEAD/S3 list requests, no credentials). Those are cited to the exact URL that was probed. Anything not verified is in "Gaps".

Site reference used for distances: 43.6442N, 78.5372E (midpoint of the 2 turbines).

---

## 1. NOAA GFS / GEFS archives (AWS, Google, Azure, NOMADS, NCAR RDA/GDEX), byte-range subsetting, availability for Jan–Feb 2026

### Takeaway
GFS 0.25° (incl. u/v at 10/20/30/40/50/80/100 m) and GEFS for every day of Jan–Feb 2026 (and back to 2023-03-11) are available **keyless** on AWS `s3://noaa-gfs-bdp-pds` / `s3://noaa-gefs-pds` and Google `gs://global-forecast-system`, with `.idx` files allowing HTTP byte-range download of only the needed GRIB2 messages; NOMADS keeps only ~10 days and the Azure GFS mirror did not have Feb 2026.

### Cited Findings
- **AWS GFS bucket has Feb 2026**: listing of `gfs.20260201/00/atmos/` returned `gfs.t00z.pgrb2.0p25.f020`…`f029` (each ~538–543 MB) plus `.idx` (~41 KB) — [S3 listing noaa-gfs-bdp-pds](https://noaa-gfs-bdp-pds.s3.amazonaws.com/?list-type=2&prefix=gfs.20260201/00/atmos/gfs.t00z.pgrb2.0p25.f02&delimiter=/)
- AWS GFS also has the start of the SCADA training period (HEAD 200 on `gfs.20230311/00/atmos/gfs.t00z.pgrb2.0p25.f024.idx`) — [object URL](https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.20230311/00/atmos/gfs.t00z.pgrb2.0p25.f024.idx)
- **Wind-relevant GRIB messages in GFS pgrb2.0p25 (2026-02-01 00z f024 .idx, 744 records)**: `UGRD/VGRD:10 m`, `:20 m`, `:30 m`, `:40 m`, `:50 m`, `:80 m`, `:100 m above ground`, `UGRD:planetary boundary layer`, `UGRD:0.995 sigma level`, `UGRD:1000/925/850 mb`, `GUST:surface`, `FRICV:surface`, `HPBL:surface`, `HGT:surface`. Example idx line: `689:497613743:d=2026020100:UGRD:100 m above ground:24 hour fcst:` (record 689 starts at byte 497,613,743) — [GFS .idx file](https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.20260201/00/atmos/gfs.t00z.pgrb2.0p25.f024.idx)
- **Google mirror has Feb 2026** (HEAD 200) — [gs://global-forecast-system object](https://storage.googleapis.com/global-forecast-system/gfs.20260201/00/atmos/gfs.t00z.pgrb2.0p25.f024.idx)
- **Azure mirror** `noaagfs.blob.core.windows.net/gfs/` returned **404 for 2026-02-01** but 200 for 2026-09-20 → only a short rolling window — [Azure 2026-02-01 (404)](https://noaagfs.blob.core.windows.net/gfs/gfs.20260201/00/atmos/gfs.t00z.pgrb2.0p25.f024.idx), [Azure 2026-09-20 (200)](https://noaagfs.blob.core.windows.net/gfs/gfs.20260920/00/atmos/gfs.t00z.pgrb2.0p25.f024.idx)
- **NOMADS retention ≈10 days**: on 2026-09-23 the directory listed `gfs.20260914` … `gfs.20260923` — [NOMADS gfs/prod](https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/)
- Herbie's GFS source priority & URL templates: `aws` `https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.{date}/...`, `google` `https://storage.googleapis.com/global-forecast-system/...`, `azure` `https://noaagfs.blob.core.windows.net/gfs/...`, `nomads`, `ftpprd`, `ncar_rda` `https://data.rda.ucar.edu/d084001/{year}/{date}/...`; products `pgrb2.0p25`, `pgrb2b.0p25`, `pgrb2.0p50`, `pgrb2full.0p50`, `sfluxgrb`, … — [Herbie GFS page](https://herbie.readthedocs.io/en/stable/gallery/noaa_models/gfs.html)
- NCAR **d084001** (GFS 0.25° historical archive): 3-hourly 0–240 h, 12-hourly 240–384 h; GDEX/CDG migrated into RDA on 2025-08-27; dataset note says a continuously-updating copy is on AWS so **RDA will stop updating d084001 in early 2026** — [GDEX d084001](https://gdex.ucar.edu/datasets/d084001/) (via search snippet), [RDA d084001 data access](https://rda.ucar.edu/datasets/d084001/dataaccess/), [THREDDS catalog](https://thredds.rda.ucar.edu/thredds/catalog/catalog_d084001.html)
- **GEFS on AWS for Feb 2026**: `gefs.20260201/00/atmos/` contains `pgrb2ap5/`, `pgrb2bp5/`, `pgrb2sp25/`, `bufr/`, `init/` (+ `chem/`, `wave/`) — [S3 listing noaa-gefs-pds](https://noaa-gefs-pds.s3.amazonaws.com/?list-type=2&prefix=gefs.20260201/00/atmos/&delimiter=/)
- GEFS `pgrb2sp25` (0.25°) files are ~17.6 MB per member per 3-h step (e.g. `geavg.t00z.pgrb2s.0p25.f021`, f024, f027 …) — [S3 listing](https://noaa-gefs-pds.s3.amazonaws.com/?list-type=2&prefix=gefs.20260201/00/atmos/pgrb2sp25/geavg.t00z.pgrb2s.0p25.f02&max-keys=6)
- GEFS `pgrb2s.0p25` contains **only 10 m wind** (`UGRD/VGRD:10 m above ground`), `GUST:surface`, TMP/DPT/RH 2 m, PRES/PRMSL, fluxes, CAPE, PWAT, etc. — **no 100 m wind** (38 records) — [gep01 f024 .idx](https://noaa-gefs-pds.s3.amazonaws.com/gefs.20260201/00/atmos/pgrb2sp25/gep01.t00z.pgrb2s.0p25.f024.idx)
- AWS registry pages: [NOAA GFS](https://registry.opendata.aws/noaa-gfs-bdp-pds/), [NOAA GEFS](https://registry.opendata.aws/noaa-gefs/)

### Inferences
- **Byte-range recipe (no special tools)**: read `.idx`, take start offset of the wanted record and the start offset of the next record − 1, then `curl -r START-END -o part.grib2 https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.20260201/00/atmos/gfs.t00z.pgrb2.0p25.f024`. For the 4 messages 10u/10v/100u/100v this is a few MB instead of ~540 MB per step. Herbie does exactly this with `H.download(":[UV]GRD:(10|100) m above")` (regex on idx lines).
- For a 24–48 h day-ahead issued "as of" day D, a practical keyless set is the latest GFS cycle published before the issue time (00z/06z/12z/18z), lead times ~f024–f054. GFS 0.25 files are **hourly** in this lead range (f020, f021 … f029 all verified to exist); hourly output to f120 is the standard GFS configuration (not re-verified beyond f029 here), so hourly features need no temporal interpolation.
- Ensemble spread for probabilistic features: GEFS pgrb2sp25 only has 10 m winds; if 100 m or PBL wind is needed from GEFS, check `pgrb2bp5`/`pgrb2ap5` (0.5°) idx first.
- Since NOMADS keeps 10 days and Azure is short-rolling, reproducible backtests must point to AWS or Google.

### Gaps
- Exact GFS product latency (when the f024–f048 files of each cycle appear on AWS relative to cycle time) was not measured; needed to define the "issue time" cutoff (commonly ~3.5–5 h after cycle, unverified).
- Contents of GEFS `pgrb2ap5`/`pgrb2bp5` (whether 100 m / 80 m winds exist) not checked.
- NCEI's own GFS archive (NCEI "Grid 4" / AIRS) not checked.
- kerchunk/VirtualiZarr references for GFS: not researched here (no source fetched).

---

## 2. ECMWF: open data (IFS, AIFS), cloud mirrors & historical archive, TIGGE/MARS/ECDS, ERA5 via CDS and keyless ARCO-ERA5

### Takeaway
ECMWF open data (CC-BY-4.0, **no key**) for Feb 2026 is archived on Google Cloud (`storage.googleapis.com/ecmwf-open-data`) and AWS (`s3://ecmwf-forecasts`) and contains IFS HRES, IFS ENS and AIFS at 0.25° **with 100u/100v and 10fg**; the ECMWF server itself keeps only ~2–4 days. The AWS mirror returned `503 SlowDown` during tests while Google worked; Azure (Planetary Computer) returned 409. TIGGE moved to the new ECMWF Data Store (ECDS, account needed); ERA5 via CDS needs a personal token, but ERA5 is also keyless on GCS (ARCO-ERA5) and on AWS (NSF NCAR).

### Cited Findings
**Open data – product definition**
- Open data: IFS HRES + ENS, AIFS single + AIFS ENS; 0.25° GRIB2; runs 00/06/12/18 UTC; IFS 00z/12z: 0–144 h every 3 h then 150–360 h every 6 h; IFS 06z/18z: 0–144 h every 3 h; AIFS 0–360 h every 6 h; params include `10u,10v,100u,100v` and wind speed; ECMWF's own server keeps "the most recent 12 forecast runs … approximately 2–3 days"; mirrored on AWS, Azure, GCP; licence CC-BY-4.0; from **13 May 2026** `scda`/`scwv` streams were discontinued and 06z/18z moved to `stream=oper` — [ECMWF open data page](https://www.ecmwf.int/en/forecasts/datasets/open-data)
- Data appear "between 7 and 9 hours after the forecast starting date and time"; client `pip install ecmwf-opendata`; `source` = `ecmwf` | `aws` | `azure` | `google`; models `ifs`, `aifs-single`, `aifs-ens`; streams `oper, wave, enfo, waef, scda, scwv`; types `fc, cf, pf, em, es, ep, tf`; if date/time omitted it fetches the latest run — [ecmwf-opendata GitHub](https://github.com/ecmwf/ecmwf-opendata)
- Herbie ECMWF: `model="ifs"` / `model="aifs"`; products `oper`, `enfo`, `wave`, `scda` (06/18z short cut-off), `scwv`, `waef`; sources: `ecmwf` last ~4 days, `azure` from **2022-01-21**, `aws` from **2023-01-18**; IFS 0.4° (`0p4-beta`) from 2023-01-18, IFS 0.25° + AIFS from **2024-02-01**, 0.4° discontinued May 2024, AIFS ENS 0.25° from 2025-07-02 — [Herbie ECMWF page](https://herbie.readthedocs.io/en/stable/gallery/ecmwf_models/ecmwf.html)
- ECMWF made its **entire Real-time Catalogue open (CC-BY-4.0) on 1 Oct 2025**; full high-volume delivery may carry service charges; free online subset is 25 km (0.25°); a 9 km subset with ~2 h latency announced for "later in 2026" — [ECMWF news](https://www.ecmwf.int/en/about/media-centre/news/2025/ecmwf-makes-its-entire-real-time-catalogue-open-all)

**Open data – verified archive contents for the test period (probed 2026-09-23)**
- AWS `ecmwf-forecasts` bucket (eu-central-1): `20260201/00z/` has sub-folders `aifs-ens/`, `aifs-single/`, `ifs/` — [S3 listing](https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/?list-type=2&prefix=20260201/00z/&delimiter=/)
- File naming: `20260201/00z/ifs/0p25/oper/20260201000000-24h-oper-fc.grib2` (~119–128 MB/step) + `.index` (~35 KB, JSON-lines); steps 0,3,…,144,150,156… — [S3 listing ifs/0p25/oper](https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/?list-type=2&prefix=20260201/00z/ifs/0p25/oper/&max-keys=40)
- **AWS returned HTTP 503 `SlowDown` ("Please reduce your request rate")** for `.index` objects of 2025-02-01, 2026-02-01 and 2026-09-22 on repeated attempts — [example object](https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/20260201/00z/ifs/0p25/oper/20260201000000-24h-oper-fc.index)
- **Google mirror works**: `https://storage.googleapis.com/ecmwf-open-data/20260201/00z/ifs/0p25/oper/20260201000000-24h-oper-fc.index` → 200; surface params at step 24: `10u,10v,100u,100v,10fg,2t,2d,msl,sp,skt,tcc,tp,ssrd,strd,…,mucape,ptype,lsm` (35 sfc params, plus `pl` and `sol` levtypes). Example line: `{"date":"20260201","time":"0000","stream":"oper","type":"fc","step":"24","levtype":"sfc","param":"100u","_offset":41298291,"_length":1405605}` (→ 100u message ≈1.4 MB of a ~127 MB file) — [GCS index](https://storage.googleapis.com/ecmwf-open-data/20260201/00z/ifs/0p25/oper/20260201000000-24h-oper-fc.index)
- Feb 2026 also on GCS: **AIFS single** `aifs-single/0p25/oper` (sfc incl. `10u,10v,100u,100v,2t,msl,sp,tcc,ssrd…`, type fc) — [GCS AIFS index](https://storage.googleapis.com/ecmwf-open-data/20260201/00z/aifs-single/0p25/oper/20260201000000-24h-oper-fc.index); **IFS 06z short cut-off** `06z/ifs/0p25/scda/…-scda-fc` with `100u/100v/10fg` — [GCS scda index](https://storage.googleapis.com/ecmwf-open-data/20260201/06z/ifs/0p25/scda/20260201060000-24h-scda-fc.index); **IFS ENS** `enfo/…-enfo-ef` with types `cf,pf` and `100u/100v/10fg` (8,160 index lines ≈ 51 members) — [GCS enfo index](https://storage.googleapis.com/ecmwf-open-data/20260201/00z/ifs/0p25/enfo/20260201000000-24h-enfo-ef.index)
- GCS mirror earliest date prefix: `20230712/` — [GCS JSON listing](https://storage.googleapis.com/storage/v1/b/ecmwf-open-data/o?delimiter=/&maxResults=5&fields=prefixes)
- **History of 100 m wind in open data** (GCS index probes, 00z, step 24): IFS 0p25 on 2024-03-01 had only `tp,st,sp,msl,skt,2t,10v,10u,tcwv,lsm,ro` (no 100u) — [2024-03-01 index](https://storage.googleapis.com/ecmwf-open-data/20240301/00z/ifs/0p25/oper/20240301000000-24h-oper-fc.index); IFS had `100u` on 2024-04-01 and every later probe (2024-05…2025-12); `10fg` absent on 2024-09-01, present from 2024-11-15 — e.g. [2024-04-01 index](https://storage.googleapis.com/ecmwf-open-data/20240401/00z/ifs/0p25/oper/20240401000000-24h-oper-fc.index)
- AIFS folder naming changed: `…/00z/aifs/0p25/oper/` (no 100u) existed 2024-04…2025-02-15; `…/00z/aifs-single/0p25/oper/` (with 100u) exists from 2025-03-01 onward — [2025-03-01 aifs-single index](https://storage.googleapis.com/ecmwf-open-data/20250301/00z/aifs-single/0p25/oper/20250301000000-24h-oper-fc.index), [2024-09-01 aifs index](https://storage.googleapis.com/ecmwf-open-data/20240901/00z/aifs/0p25/oper/20240901000000-24h-oper-fc.index)
- Azure mirror `https://ai4edataeuwest.blob.core.windows.net/ecmwf/…` returned **HTTP 409** for anonymous requests (Feb 2026 IFS, AIFS, scda) — [example](https://ai4edataeuwest.blob.core.windows.net/ecmwf/20260201/00z/ifs/0p25/oper/20260201000000-24h-oper-fc.index)

**TIGGE / MARS / ECDS**
- TIGGE: registration required, data with **48 h delay** — [TIGGE FAQ](https://confluence.ecmwf.int/display/TIGGE/FAQ), [TIGGE licence](https://apps.ecmwf.int/datasets/data/tigge/licence/)
- New **ECMWF Data Store (ECDS)** launched **2026-04-21**; TIGGE/S2S moved there; old **Web-API decommissioned 2026-05-27**; users must migrate to the CDS-API style client; ECMWF login needed — [ECMWF forum announcement](https://forum.ecmwf.int/t/s2s-and-tigge-access-method/15020), portal [ecds.ecmwf.int](https://ecds.ecmwf.int/)

**ERA5 via CDS (key required)**
- CDS: account + personal access token; `~/.cdsapirc` = `url: https://cds.climate.copernicus.eu/api` / `key: <PERSONAL-ACCESS-TOKEN>`; `cdsapi>=0.7.7`; **each dataset's Terms of Use must be accepted manually on the web page**; newer `ecmwf-datastores-client` optional (status "Incubating") — [CDS how-to-api](https://cds.climate.copernicus.eu/how-to-api)
- **ERA5 hourly time-series on single levels** (`reanalysis-era5-single-levels-timeseries`): ARCO point-optimised subset of ERA5 0.25°, 1940→present, ~5 days behind real time, CSV or netCDF, nearest grid point, "experimental", published 2025-03-18 — [CDS dataset](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-timeseries?tab=overview), [ECMWF forum](https://forum.ecmwf.int/t/new-dataset-published-in-cds-era5-hourly-time-series-data-on-single-levels-from-1940-to-present/11919). Analogue for ERA5-Land: [reanalysis-era5-land-timeseries](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries?tab=overview)

**ERA5 keyless**
- **ARCO-ERA5** on GCS `gs://gcp-public-data-arco-era5` (us-central1), anonymous (`storage_options=dict(token='anon')`), no requester-pays; `ar/full_37-1h-0p25deg-chunk-1.zarr-v3` (37 pressure levels + surface, 2.05 PB, chunks `{time:1, lat:721, lon:1440}`), `ar/model-level-1h-0p25deg.zarr-v1`, `co/single-level-*`, `raw/`; ERA5 final updated monthly with ~3-month delay, ERA5T ~1 week latency; attrs `valid_time_stop`, `valid_time_stop_era5t` — [google-research/arco-era5](https://github.com/google-research/arco-era5)
- **NSF NCAR ERA5 on AWS** `s3://nsf-ncar-era5` (anonymous): monthly per-variable global NetCDF, e.g. `e5.oper.an.sfc/202602/e5.oper.an.sfc.228_246_100u.ll025sc.2026020100_2026022823.nc` (1.40 GB), `…228_247_100v…` (1.43 GB), `…128_165_10u…`, `…128_166_10v…`, `…128_134_sp…`, `…128_167_2t…`; latest month present on 2026-09-23 = **2026-06** — [S3 listing 2026](https://nsf-ncar-era5.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=e5.oper.an.sfc/2026), [S3 listing 202602](https://nsf-ncar-era5.s3.amazonaws.com/?list-type=2&prefix=e5.oper.an.sfc/202602/&max-keys=200)

### Inferences
- **For the backtest use `source="google"`** (or raw HTTPS to `storage.googleapis.com/ecmwf-open-data`) rather than AWS to avoid 503 SlowDown; implement retry/backoff anyway.
- Example (keyless) — 100 m wind for the 00z run of 2026-02-01, steps 24–48:
  ```python
  from ecmwf.opendata import Client
  c = Client(source="google", model="ifs", resol="0p25")
  c.retrieve(date="2026-02-01", time=0, stream="oper", type="fc",
             step=list(range(24, 49, 3)), param=["10u","10v","100u","100v","10fg","2t","msl"],
             target="ifs_20260201_00.grib2")
  ```
  For 06z/18z in Feb 2026 use `stream="scda"` (pre-May-2026 naming); AIFS: `model="aifs-single"` (6-hourly steps).
- Because IFS 00z is published ~7–9 h after 00 UTC (≈12–14 local time, UTC+5), a forecast "as of" the morning of day D would have to use the previous day's 12z (or 18z scda) run; 24–48 h ahead then requires steps ~30–60 h.
- 100 m wind features from ECMWF open data are consistent only from ~2024-04 (IFS) and 2025-03 (AIFS-single); for the SCADA training window starting 2023-03, IFS 0.4° (2023) and early 0.25° (to 2024-03) offer only 10 m wind → either restrict training of ECMWF-based models to ≥2024-04 or use 10 m winds only.
- ARCO-ERA5 time-chunk=1 layout is inefficient for a 3-year single-point series (tens of thousands of ~150 MB chunks); for a point, prefer (a) the CDS time-series dataset (needs key), (b) NASA POWER (MERRA-2, keyless, see §7), or (c) NCAR AWS monthly files with byte-range/HDF5 partial reads.
- Reanalysis (ERA5/ERA5T) must **not** be used as a predictor at forecast time in the Feb 2026 test (it is not a forecast available at issue time); it is only usable for training-time diagnostics, height-extrapolation/shear climatology or gap-filling targets.

### Gaps
- Whether `ecmwf-opendata` still resolves Feb-2026 `scda` paths after the May-2026 stream change was not tested in code (only raw paths were probed).
- Exact steps of 06z/18z `scda` runs in Feb 2026 (historically 0–90 h) not verified; ECMWF page now states 0–144 h for 06/18z (post-change).
- Why Azure returned 409 (probably Planetary Computer SAS-token requirement) — not verified.
- Whether 10 m / 100 m ENS mean products (`em`/`es`) are available in the archive for Feb 2026 — not probed.
- ECMWF 9 km open-data subset: announced for "later in 2026"; current status not verified.

---

## 3. DWD ICON, UK Met Office and other NWP

### Takeaway
DWD ICON open data is real-time only (24 h retention) — useless for a Feb-2026 backtest unless someone archived it; no official public archive exists. Other NWP (UKMO, ECCC, JMA, CMA) were not verified in this session.

### Cited Findings
- DWD NWP open data at `https://opendata.dwd.de/weather/nwp/`; raw files are deleted after ~24 h, no long-term public archive; Open Climate Fix published community archives on Hugging Face (`openclimatefix/dwd-icon-global`, `openclimatefix/dwd-icon-eu`) — [open-meteo/open-data README (search summary)](https://github.com/open-meteo/open-data/blob/main/README.md), [HF dwd-icon-global](https://huggingface.co/datasets/openclimatefix/dwd-icon-global), [DWD NWP data page](https://www.dwd.de/EN/ourservices/nwp_forecast_data/nwp_forecast_data.html)
- Herbie also supports ECCC GDPS/GEPS/RDPS/HRDPS and US Navy NAVGEM — [Herbie gallery](https://herbie.readthedocs.io/en/stable/gallery/index.html)

### Inferences
- For Feb 2026 hindcasts the realistic keyless multi-model set is: GFS (+GEFS), ECMWF IFS/ENS/AIFS (open-data archive), NOAA GraphCast-GFS (see §4). ICON would require a third-party archive whose Feb-2026 coverage is unknown.

### Gaps
- Coverage period of the OCF ICON-global Hugging Face archive (does it include Feb 2026?) not checked.
- UK Met Office global model on AWS (Met Office "atmospheric model data" open data) — retention/archival for Feb 2026 not researched.
- ECCC MSC Datamart retention (~1–2 days) not verified; CMA/JMA not researched.

---

## 4. Tools (Herbie, ecmwf-opendata, cfgrib/eccodes, kerchunk, earthkit) and archived AI-model forecasts for 2026

### Takeaway
Herbie 2026.9.1 covers GFS/GEFS/AIGFS/AIGEFS/HGEFS/IFS/AIFS with idx-based subsetting and `pick_points`; for AI forecasts, **NOAA GraphCast-GFS daily runs covering all of 2025 and Jan–May 2026 are keyless on AWS**, ECMWF AIFS-single is in the ECMWF open-data archive, while operational AIGFS on AWS only starts 2026-04-16 and Google WeatherNext requires a GCP account/data-request.

### Cited Findings
**Herbie**
- `herbie-data` latest **2026.9.1 (2026-09-20)**, Python ≥3.11, MIT; `pip install herbie-data` / `conda install -c conda-forge herbie-data` / `uv add herbie-data`; models: HRRR, RAP, NAM, NBM, RTMA/URMA, RRFS, HAFS, **GFS, GEFS, AIGFS, AIGEFS, HGEFS, CFS**, ECMWF **IFS, AIFS**, HRDPS, NAVGEM; sources: NOMADS, NODD (AWS/Google/Azure), ECMWF open data, Utah Pando, local; wgrib2 optional; example `H = Herbie('2023-03-15 12:00', model='gfs', product='0p25', fxx=24); ds = H.xarray(':500 mb')` — [PyPI herbie-data](https://pypi.org/project/herbie-data/)
- `ds.herbie.pick_points(points_df, method="nearest"|"weighted", k=…)`: nearest → k=1, weighted → inverse-distance mean of 4 nearest; uses scikit-learn **BallTree** (haversine), works for any grid projection, cached tree (`tree_name`), returns `point_latitude`, `point_longitude`, `point_grid_distance` (km) — [Herbie Pick Points](https://herbie.readthedocs.io/en/stable/user_guide/tutorial/accessor_notebooks/pick_points.html), [HerbieAccessor API](https://herbie.readthedocs.io/en/stable/api_reference/_autosummary/herbie.accessors.HerbieAccessor.html)
- Herbie search uses regex on idx lines, e.g. `:10[uv]:`, `:2t:` (eccodes-style for ECMWF) — [Herbie ECMWF page](https://herbie.readthedocs.io/en/stable/gallery/ecmwf_models/ecmwf.html)

**NOAA AI models**
- NCEP implemented **AIGFS, AIGEFS (31 members) and HGEFS (62-member hybrid)** operationally on **2025-12-17**; 0.25°, 4 cycles/day, 6-hourly to 384 h — [NOAA news release](https://www.noaa.gov/news-release/noaa-deploys-new-generation-of-ai-driven-global-weather-models), [EPIC](https://epic.noaa.gov/noaa-deploys-new-ai-driven-global-weather-models/), [GribStream blog (secondary)](https://gribstream.com/blog/noaa-ai-gfs-aigfs-aigefs-hgefs-operational)
- AWS bucket `s3://noaa-nws-graphcastgfs-pds` (now branded "NOAA EAGLE") — [AWS registry](https://registry.opendata.aws/noaa-nws-graphcastgfs-pds/)
- Probed root listing (2026-09-23): prefixes `EAGLE_ensemble/`, `Truth_Zarr/`, `aigfs.20260416/` … (**AIGFS only from 2026-04-16**, nothing for Feb 2026) — [S3 root listing](https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com/?list-type=2&delimiter=/&max-keys=30), [aigfs.202602* empty](https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=aigfs.2026020)
- **GraphCast-GFS archive**: `graphcastgfs.YYYYMMDD/` for all 365 days of 2025 and 125 days of 2026 (2026-01-01 … 2026-05-05) — [listing 2025](https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=graphcastgfs.2025), [listing 2026](https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=graphcastgfs.2026)
- Files: `graphcastgfs.20260201/00/forecasts_13_levels/graphcastgfs.t00z.pgrb2.0p25.f000, f006, f012, f018, f024, f030…` (~85 MB each, with `.idx`) — [listing 2026-02-01](https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com/?list-type=2&prefix=graphcastgfs.20260201/&max-keys=12)
- `EAGLE_ensemble/` holds experimental `aigefs.20250601/`… and `pmlgefs.…` up to `pmlgefs.20251218/` — [listing](https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=EAGLE_ensemble/)
- Secondary source: HGEFS not visible on S3, only via NOMADS — [GribStream blog](https://gribstream.com/blog/noaa-eagle-aigfs-aigefs-current-forecasts-aws)

**ECMWF AIFS** — archived in ECMWF open data (see §2): `aifs-single` Feb 2026 with 100u/100v; AIFS-ENS from 2025-07-02 — [Herbie ECMWF](https://herbie.readthedocs.io/en/stable/gallery/ecmwf_models/ecmwf.html), [S3 listing 20260201/00z](https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/?list-type=2&prefix=20260201/00z/&delimiter=/)

**Google WeatherNext**
- WeatherNext 2 (FGN, 0.25°, 6-hourly, 64 members, 15-day, every 6 h) in **BigQuery and Earth Engine**; historic experimental 2022→present Zarr at `gs://weathernext/weathernext_2_0_0/zarr` requires the **WeatherNext Data Request form**; forecasts >48 h old CC-BY-4.0, real-time under GDM experimental terms; WeatherNext 3 also documented — [WeatherNext BigQuery guide](https://developers.google.com/weathernext/guides/bigquery), [WeatherNext models](https://developers.google.com/weathernext/guides/models), [EE catalog WeatherNext 2](https://developers.google.com/earth-engine/datasets/catalog/projects_gcp-public-data-weathernext_assets_weathernext_2_0_0), [GitHub google-deepmind/weathernext](https://github.com/google-deepmind/weathernext)

### Inferences
- GraphCast-GFS gives a keyless **AI forecast archive covering the whole Feb-2026 test month** (6-hourly, 0.25°, 13 pressure levels + surface; likely 10 m winds only — verify idx). AIGFS/AIGEFS operational archives do not cover Feb 2026 on AWS.
- WeatherNext requires a Google Cloud project/Earth Engine registration (+ BigQuery billing) → not usable by evaluators without accounts; could be used offline only if pre-extracted data are shipped with the solution (check CC-BY attribution).
- Windows: cfgrib needs the ecCodes binary; conda-forge (`conda install -c conda-forge eccodes cfgrib`) is the usual path; recent `eccodes` Python wheels bundle the library (unverified here).

### Gaps
- GraphCast-GFS idx variable list (does it have 10 m u/v; any 100 m?) not probed.
- WeatherBench2 archived AI forecasts (GraphCast/Pangu/FourCastNet on `gs://weatherbench2`) — period coverage not checked (believed to end ~2022/2023, i.e., irrelevant for Feb 2026; unverified).
- Pangu/FourCastNet/Aurora 2026 archives: none found in this session.
- kerchunk / VirtualiZarr / earthkit: no documentation fetched; Windows-specific Herbie notes not found.

---

## 5. Reanalysis: ERA5, ERA5-Land, MERRA-2, CERRA, JRA-3Q — which are keyless

### Takeaway
Keyless: ERA5 via ARCO-ERA5 (GCS) and NSF NCAR (AWS); MERRA-2 indirectly via NASA POWER API. Key/registration needed: CDS (ERA5, ERA5-Land, time-series datasets), MERRA-2 native (NASA Earthdata Login), JRA-3Q (GDEX; non-commercial licence). CERRA covers Europe only (not this site).

### Cited Findings
- ERA5 keyless options and latency — see §2: [ARCO-ERA5](https://github.com/google-research/arco-era5), [nsf-ncar-era5 S3](https://nsf-ncar-era5.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=e5.oper.an.sfc/2026)
- ERA5 / ERA5-Land point time-series datasets on CDS (key needed) — [ERA5 TS](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-timeseries?tab=overview), [ERA5-Land TS](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries?tab=overview), [family of ERA5 datasets](https://confluence.ecmwf.int/display/CKB/The+family+of+ERA5+datasets)
- MERRA-2 `M2T1NXSLV` (tavg1_2d_slv_Nx): hourly, 0.625°×0.5°, includes wind at **2, 10, 50 m** and 850/500/250 hPa; **Earthdata Login required** and must be linked to GES DISC; OPeNDAP subsetting available; also listed on AWS registry and Earth Engine — [Earthdata catalog M2T1NXSLV](https://www.earthdata.nasa.gov/fr/data/catalog/ges-disc-m2t1nxslv-5.12.4), [AWS registry nasa-m2t1nxslv](https://registry.opendata.aws/nasa-m2t1nxslv/), [EE catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_GSFC_MERRA_slv_2), [Earthdata forum FAQ](https://forum.earthdata.nasa.gov/viewtopic.php?t=5678)
- JRA-3Q at NSF NCAR GDEX `d640000` (DOI 10.5065/AVTZ-1H78), 471.84 TB, HTTPS (OSDF) / Globus; **CC-BY-NC-SA 4.0, free for non-commercial use** — [GDEX d640000 data access](https://gdex.ucar.edu/datasets/d640000/dataaccess/), [JMA JRA-3Q](https://www.data.jma.go.jp/jra/html/JRA-3Q/index_en.html), [Climate Data Guide](https://climatedataguide.ucar.edu/climate-data/jra-3q-atmospheric-reanalysis)
- MERRA-2 values are served keylessly through NASA POWER hourly API (sources `MERRA2`, `POWER`) — verified, see §7 — [POWER request](https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=WS10M,WD10M,WS50M,WD50M&community=RE&longitude=78.5372&latitude=43.6442&start=20260201&end=20260202&format=JSON&time-standard=UTC)

### Inferences
- CERRA (Copernicus European Regional Reanalysis) domain is Europe → does not cover Kazakhstan (general knowledge, not re-verified).
- JRA-3Q's non-commercial licence may conflict with a commercial wind-farm use case; ERA5 (Copernicus licence, CC-BY-like) and MERRA-2 (NASA, open) are safer.
- None of the reanalyses is a legitimate predictor at forecast time; they are for training diagnostics (e.g., learning ERA5-100 m ↔ SCADA transfer functions, shear exponent climatology) only.

### Gaps
- Whether GDEX d640000 downloads require an NCAR/ORCID login in 2026 was not verified.
- Whether AWS-hosted MERRA-2 (NASA Earthdata Cloud) allows anonymous reads — not verified (typically requires Earthdata temporary S3 credentials).
- ERA5-Land has no 100 m wind (10 m only) — general knowledge, not re-verified.

---

## 6. Surface observations near the site (Kazhydromet stations, NOAA ISD/GHCNh, Meteostat, OGIMET, rp5)

### Takeaway
The nearest synoptic stations are **WMO 36894 (listed as MALIBAY/"Шелек", ~21–24 km)** and **36891 (CILIK/Chilik, ~28 km)**; their 3-hourly SYNOP wind for Jan–Sep 2026 is available **keyless in NOAA GHCNh** (PSV files updated 2026-09-21). Legacy **ISD global-hourly stopped at Aug/Oct 2025 (no 2026 folder)**, and **Meteostat's 2026 data for 36894 is 100 % MET Norway model forecast, not observations** — must filter by `*_source`.

### Cited Findings
**Station inventory (NOAA ISD history, filtered 42.3–45.5N, 76–81.5E; distance from site computed)** — [isd-history.csv](https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv)

| USAF/WMO | Name | Lat | Lon | Elev m | ISD BEGIN–END | km |
|---|---|---|---|---|---|---|
| 368940 / 36894 | MALIBAY | 43.483 | 78.400 | 870 | 1959-01-01 – 2025-08-24 | 21.1 |
| 368910 / 36891 | CILIK | 43.583 | 78.200 | 600 | 1981-01-01 – 2025-08-24 | 28.0 |
| 368970 / 36897 | ASSI | 43.317 | 78.250 | 2216 | 1957 – 2022-12-31 | 43.1 |
| 369050 / 36905 | PODGORNOJE | 43.317 | 79.483 | 1273 | 1959 – 2025-08-24 | 84.4 |
| 368890 / 36889 | TURGEN | 43.383 | 77.550 | 980 | 1959 – 2025-08-24 | 84.6 |
| 368850 / 36885 | ISSYK (Esik) | 43.350 | 77.467 | 1098 | 1959 – 2025-08-24 | 92.1 |
| 368560 / 36856 | KONYROLEN | 44.267 | 79.317 | 1224 | 2013 – 2025-08-24 | 93.5 |
| 368720 / UAAA | ALMATY airport | 43.352 | 77.041 | 681 | 2006 – 2025-08-24 | 124.7 |
| 368590 / 36859 | ZHARKENT | 44.167 | 80.067 | 645 | 1946 – 2025-08-24 | 136.1 |
| 368700 / 36870 | ALMATY | 43.233 | 76.933 | 851 | 1932 – 2025-08-24 | 136.9 |
| 368810 / 36881 | KAPCAGAJ | 43.883 | 77.067 | 456 | 1959 – 2002-12-23 | 121.2 |

- GHCNh station list additionally shows **KZM00036907 KEGEN** (43.000N 79.200E, 1845 m) and a legacy entry **KZU00036894 "CHILIK USSR" at 43.600N 78.250E, 608 m** — [ghcnh-station-list.txt](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh-station-list.txt)
- Russian-language sites label **36894 as "Шелек"** — [pogodaiklimat.ru id=36894](http://www.pogodaiklimat.ru/weather.php?id=36894), [rp5.kz "Погода в Шелеке (метеостанция 36894)"](http://rp5.kz/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%A8%D0%B5%D0%BB%D0%B5%D0%BA%D0%B5_(%D0%BC%D0%B5%D1%82%D0%B5%D0%BE%D1%81%D1%82%D0%B0%D0%BD%D1%86%D0%B8%D0%B8_36894)); **conflict**: NOAA metadata places 36894 at "MALIBAY" 43.483N 78.400E 870 m.

**ISD (legacy) status**
- `global-hourly/access/2026/…csv` returns **404** even for LaGuardia (72503014732); 2025 files for 36894/36891 exist with Last-Modified **2025-10-01** — [2026 36894 (404)](https://www.ncei.noaa.gov/data/global-hourly/access/2026/36894099999.csv), [2026 LGA (404)](https://www.ncei.noaa.gov/data/global-hourly/access/2026/72503014732.csv), [2025 36894 (200)](https://www.ncei.noaa.gov/data/global-hourly/access/2025/36894099999.csv)

**GHCNh (successor, keyless) — verified content**
- URL pattern: `https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year/{YYYY}/psv/GHCNh_{ID}_{YYYY}.psv`; 2026 files for KZM00036894, KZM00036891, KZM00036870, KZM00036885, KZI0000UAAA all 200, Last-Modified **2026-09-21**; 2025 files Last-Modified 2026-07-11 — [GHCNh 36894 2026](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year/2026/psv/GHCNh_KZM00036894_2026.psv), [GHCNh 36891 2026](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year/2026/psv/GHCNh_KZM00036891_2026.psv), [GHCNh UAAA 2026](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year/2026/psv/GHCNh_KZI0000UAAA_2026.psv)
- PSV format: 329 columns, `STATION|Station_name|DATE|Year|Month|Day|Hour|Minute|LATITUDE|LONGITUDE|ELEVATION|temperature|temperature_Measurement_Code|temperature_Quality_Code|…|wind_direction|wind_speed|wind_gust|…` (same source as above).
- **Feb 2026 rows**: 36894 = 201 (synoptic hours 00/06/09/12/21 ≈28 each, 03/15 ≈16–18); 36891 = 204; 36870 = 200. Wind speed in whole m/s, direction in degrees, `999` for calm/variable; e.g. 36894 2026-02-01 00Z ws=1.0 wd=120, 03Z ws=2.0 wd=070, 09Z ws=3.0 wd=090. 2026 rows/month for 36894: Jan 233, Feb 201, Mar 195, Apr 234, May–Aug 240–248, Sep 152 (last obs 2026-09-19 21Z); 36891 last obs **2026-07-19 15Z** (source: same GHCNh files).
- ISD Almaty airport (UAAA) has METAR-frequency data (2026 file ~9.6 MB vs ~1.3 MB for SYNOP stations) (source: same HEAD results).

**Meteostat**
- Python library `meteostat` **2.1.5**, Python ≥3.11 — [PyPI meteostat JSON](https://pypi.org/pypi/meteostat/json)
- Library is keyless ("unlimited data access… doesn't require users to sign up"), built on the bulk interface; the JSON API (RapidAPI) needs a key — [Meteostat blog / dev docs](https://dev.meteostat.net/python), [Meteostat stable release post](https://meteostat.net/en/blog/python-library-stable-release)
- New bulk endpoint `https://data.meteostat.net/hourly/{year}/{wmo}.csv.gz` (36894 2026 file Last-Modified 2026-09-23) with columns `year,month,day,hour,temp,temp_source,rhum,…,wdir,wdir_source,wspd,wspd_source,pres,…,coco,coco_source`; legacy `bulk.meteostat.net/v2/hourly/2026/36894.csv.gz` is stale (last row 2026-03-19, Last-Modified 2026-03-10) — [data.meteostat.net 36894 2026](https://data.meteostat.net/hourly/2026/36894.csv.gz), [bulk v2 36894 2026](https://bulk.meteostat.net/v2/hourly/2026/36894.csv.gz)
- **Source audit for 36894** (`wspd_source` counts): 2026 → 6,400/6,400 rows `metno_forecast` (Feb: 628 rows, all model); 2025 → `isd_lite` 1,798 vs `metno_forecast` 6,853 (Feb: 209 obs vs 463 model); 2024 → `isd_lite` 2,631 vs `metno_forecast` 5,985 — [data.meteostat.net 2025](https://data.meteostat.net/hourly/2025/36894.csv.gz), [2024](https://data.meteostat.net/hourly/2024/36894.csv.gz)

**Kazhydromet (РГП «Казгидромет»)**
- Official meteorological DB portal `https://meteo.kazhydromet.kz/database_meteo` (and hydrological `…/database_hydro`): "общего назначения" data from state network, **2000 → present, updated monthly**, **registration required**, attribution mandatory; contacts info@meteo.kz — [kazhydromet.kz/ru/meteo_db](https://www.kazhydromet.kz/ru/meteo_db), [meteo.kazhydromet.kz/database_meteo](https://meteo.kazhydromet.kz/database_meteo)
- Climate page for Almaty; Almaty-region branch history mentions Assy agro-station (Enbekshikazakh district) — [Kazhydromet Almaty climate](https://www.kazhydromet.kz/ru/klimat/almaty), [branch history](https://www.kazhydromet.kz/ru/branches_history/14)

**OGIMET / rp5**
- OGIMET `gsynres` returned **HTTP 403** to automated fetch — [OGIMET 36894 query](https://www.ogimet.com/cgi-bin/gsynres?ind=36894&ano=2026&mes=2&day=2&hora=0&ndays=2&lang=en)
- rp5 publishes observations 8×/day (3-hourly) and allows archive export (xls/csv) via web form — [GIS-Lab forum on rp5 export](https://gis-lab.info/forum/viewtopic.php?t=19029), [rp5.kz Шелек 36894](http://rp5.kz/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%A8%D0%B5%D0%BB%D0%B5%D0%BA%D0%B5_(%D0%BC%D0%B5%D1%82%D0%B5%D0%BE%D1%81%D1%82%D0%B0%D0%BD%D1%86%D0%B8%D0%B8_36894))
- Meteomanz provides SYNOP/BUFR-decoded observations worldwide — [meteomanz.com](https://www.meteomanz.com/?l=1)

### Inferences
- **Best keyless obs source for 2023–2026 = GHCNh** (scriptable, stable URLs). Use 36894 (+36891, 36885/36889 for regional context). ISD-based tools (e.g., older Meteostat, `isd-lite`) will silently lack post-Aug-2025 observations.
- If Meteostat is used, **drop rows where `wspd_source` ≠ observation** (e.g., `metno_forecast`), otherwise you train/validate on a model product (and, for the Feb-2026 test, on data that was not an observation at issue time).
- Observations are only usable as predictors if their timestamp ≤ issue time (e.g., last SYNOP before the forecast issue: 03Z/06Z for a morning issue). Coarse 1 m/s resolution and 10 m anemometers at 600–870 m in a mountain-valley corridor → useful mainly for regime/bias features (easterly vs westerly flow), not direct hub-height wind.
- Metadata conflict (36894 "Malibay 43.48N 78.40E 870 m" vs "Шелек/Chilik 43.60N 78.25E 608 m") must be resolved before using elevation/position (e.g., check GHCNh LATITUDE/ELEVATION columns per row, or Kazhydromet station passport).

### Gaps
- Whether rp5 archive export for 36894 requires captcha/manual interaction (likely) — not tested; treat as non-automatable.
- Kazhydromet portal: temporal resolution (срочные vs суточные), wind parameters and download format behind the login not visible; AWS (automatic station) network near Shelek unknown.
- Meteostat unit of `wspd` (km/h in Meteostat convention) not re-verified in 2.x docs.
- Whether Kazhydromet shares 10-min/hourly data from any automatic station at Shelek, or local wind-farm met masts exist — not found.

---

## 7. Terrain & wind resource (Global Wind Atlas, DEM, land cover/roughness, NASA POWER)

### Takeaway
Global Wind Atlas is now **v4** with keyless country GeoTIFF downloads (`/api/gis/country/KAZ/wind-speed/100` → CDN, 177.7 MB, ZSTD-compressed float32, 0.0025° ≈ 250 m); Copernicus DEM 30 m and ESA WorldCover 10 m tiles for the site are keyless on AWS; NASA POWER hourly API (MERRA-2-based, WS10M/WS50M, keyless) returns Feb-2026 data at the site — but its grid-cell elevation (1062 m) is ~500 m above the turbines.

### Cited Findings
- `https://globalwindatlas.info/api/gis/country/KAZ/wind-speed/100` → HTTP 302 → `https://gwa.cdn.nazkamapps.com/country_tifs_v4/KAZ_wind-speed_100m.tif` — [GWA API URL](https://globalwindatlas.info/api/gis/country/KAZ/wind-speed/100)
- The KAZ 100 m file: 177,743,928 bytes, Last-Modified 2025-06-13; TIFF header (read via HTTP range): 16346×5967 px, 32-bit float, compression tag **50000 (ZSTD)**, predictor 3, tiled, pixel 0.0025°, origin lon 46.47125 / lat 55.46375, nodata NaN — [GWA v4 KAZ 100 m GeoTIFF](https://gwa.cdn.nazkamapps.com/country_tifs_v4/KAZ_wind-speed_100m.tif)
- GWA provides mean wind speed / power density at 10, 50, 100, 150, 200 m, 250 m output resolution; GeoTIFF downloads free; API "not to be used for bulk downloads" — [atlas.co summary](https://atlas.co/data-sources/global-wind-atlas/), [GWA GIS files page](https://globalwindatlas.info/download/gis-files) (JS app; content via search snippet), [GEE community catalog GWA](https://gee-community-catalog.org/projects/gwa/)
- **Copernicus DEM GLO-30** tile covering the site: `https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N43_00_E078_00_DEM/Copernicus_DSM_COG_10_N43_00_E078_00_DEM.tif` (38.5 MB, COG, anonymous) — [tile URL](https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N43_00_E078_00_DEM/Copernicus_DSM_COG_10_N43_00_E078_00_DEM.tif)
- **ESA WorldCover 10 m v200 (2021)** tile: `https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N42E078_Map.tif` (83.8 MB, anonymous) — [tile URL](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N42E078_Map.tif)
- **NASA POWER hourly API**: `https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=…&community=…&longitude=…&latitude=…&start=YYYYMMDD&end=YYYYMMDD&format=JSON|CSV|NetCDF|ASCII&time-standard=UTC|LST`; ≤15 parameters/request; hourly 2001-01-01 → near real time; wind params WS10M, WS50M, WD10M, WD50M, U10M, V10M… ; no key mentioned — [POWER hourly API docs](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/)
- Verified call (no key, `community=RE`) for 2026-02-01…02 returned API v2.10.2, `sources: ["MERRA2","POWER"]`, WS50M 2026-02-01 00–05 UTC = 1.98, 2.14, 2.52, 2.77, 2.50, 1.59 m/s; returned geometry elevation **1061.97 m** — [POWER request](https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=WS10M,WD10M,WS50M,WD50M&community=RE&longitude=78.5372&latitude=43.6442&start=20260201&end=20260202&format=JSON&time-standard=UTC)

### Inferences
- **Getting GWA point values without downloading 178 MB**: GDAL/rasterio can range-read the tiled GeoTIFF: `rasterio.open("/vsicurl/https://gwa.cdn.nazkamapps.com/country_tifs_v4/KAZ_wind-speed_100m.tif").sample([(78.535604, 43.645150), (78.538828, 43.643198)])`; repeat for `wind-speed/50`, `/150` (same URL pattern). A plain-numpy reader fails because of ZSTD (needs `zstandard`/`imagecodecs` or GDAL). File naming suggests other layers follow `{ISO3}_{layer}_{height}m.tif`.
- GWA mean speeds are long-term climatology (static) → useful for sanity checks, a static feature, or scaling/bias priors, not for hourly forecasting.
- WorldCover class → roughness length (z0) lookup + Copernicus DEM (slope, relative elevation, valley orientation) can support shear/height-extrapolation features or explain directional bias; both are static and keyless.
- POWER/MERRA-2 is a reanalysis (latency days) → training/diagnostics only; the 1062 m cell elevation indicates the 0.5°×0.625° cell mixes the Chilik valley with the Zailiysky/Ketmen foothills — expect biases vs. hub-height wind.

### Gaps
- **Actual GWA v4 values at the turbines (50/100/150 m) were not obtained**: the local venv lacked GDAL/zstd, and no public point-JSON API was found documented.
- GWA v3→v4 methodological changes and release date not documented here (only file Last-Modified 2025-06-13).
- SRTM (via OpenTopography, needs API key) not checked; Copernicus DEM is the keyless alternative.

---

## 8. Satellite / other auxiliary sources

### Takeaway
Nothing onshore-specific was found to be necessary; ASCAT/scatterometer winds are ocean-only and irrelevant. Commercial aggregators (GribStream) exist for archived NWP/AI point series but are not keyless.

### Cited Findings
- GribStream (commercial API) blog posts track NOAA AIGFS/AIGEFS availability — [GribStream AIGFS/AIGEFS archive](https://gribstream.com/blog/aigfs-aigefs-s3-archive-gribstream), [ECMWF open catalogue post](https://gribstream.com/blog/ecmwf-real-time-catalogue-open-data-2025)

### Inferences
- Satellite products are unlikely to add value for a 24–48 h hourly wind forecast at a single onshore site within hackathon scope.

### Gaps
- Commercial point-forecast archive services (Meteomatics, GribStream pricing, Visual Crossing) not evaluated; all require keys.

---

## 9. Access/auth summary (what evaluators can run without accounts)

### Takeaway
A fully keyless pipeline is possible with: GFS/GEFS (AWS/GCS), ECMWF IFS/ENS/AIFS open data archive (GCS preferred), NOAA GraphCast-GFS (AWS), GHCNh observations, NASA POWER, ARCO-ERA5/NCAR ERA5, GWA GeoTIFF, Copernicus DEM, ESA WorldCover. Everything else needs registration.

### Cited Findings
| Source | Feb-2026 coverage | Auth | Evidence |
|---|---|---|---|
| GFS 0.25 (AWS `noaa-gfs-bdp-pds`, GCS `global-forecast-system`) | yes (hourly leads; back to 2023-03-11 verified) | none | [S3](https://noaa-gfs-bdp-pds.s3.amazonaws.com/?list-type=2&prefix=gfs.20260201/00/atmos/gfs.t00z.pgrb2.0p25.f02&delimiter=/), [GCS](https://storage.googleapis.com/global-forecast-system/gfs.20260201/00/atmos/gfs.t00z.pgrb2.0p25.f024.idx) |
| GEFS (AWS `noaa-gefs-pds`) | yes | none | [S3](https://noaa-gefs-pds.s3.amazonaws.com/?list-type=2&prefix=gefs.20260201/00/atmos/&delimiter=/) |
| GFS NOMADS / Azure | no (10 d / short) | none | [NOMADS](https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/) |
| ECMWF open data IFS/ENS/AIFS (GCS `ecmwf-open-data`, AWS `ecmwf-forecasts`) | yes, incl. 100u/100v | none (CC-BY-4.0) | [GCS index](https://storage.googleapis.com/ecmwf-open-data/20260201/00z/ifs/0p25/oper/20260201000000-24h-oper-fc.index) |
| NOAA GraphCast-GFS (AWS `noaa-nws-graphcastgfs-pds`) | yes (2025-01-01…2026-05-05) | none | [S3](https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=graphcastgfs.2026) |
| NOAA AIGFS (same bucket) | no (from 2026-04-16) | none | [S3](https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com/?list-type=2&delimiter=/&max-keys=30) |
| TIGGE (ECDS) | yes (48 h delay) | ECMWF account | [forum](https://forum.ecmwf.int/t/s2s-and-tigge-access-method/15020) |
| ERA5 CDS / ERA5 time-series | yes (≈5 d lag) | CDS token + licence click | [CDS how-to](https://cds.climate.copernicus.eu/how-to-api) |
| ARCO-ERA5 (GCS) / NCAR ERA5 (AWS) | yes (ERA5T ~1 wk / NCAR to 2026-06) | none | [ARCO](https://github.com/google-research/arco-era5), [NCAR S3](https://nsf-ncar-era5.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=e5.oper.an.sfc/2026) |
| MERRA-2 native | yes | Earthdata Login | [Earthdata](https://www.earthdata.nasa.gov/fr/data/catalog/ges-disc-m2t1nxslv-5.12.4) |
| NASA POWER (MERRA-2) | yes | none | [POWER call](https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=WS10M,WD10M,WS50M,WD50M&community=RE&longitude=78.5372&latitude=43.6442&start=20260201&end=20260202&format=JSON&time-standard=UTC) |
| JRA-3Q (GDEX d640000) | n/c | CC-BY-NC-SA; login status unverified | [GDEX](https://gdex.ucar.edu/datasets/d640000/dataaccess/) |
| WeatherNext 2/3 | yes (2022→) | GCP/EE account, data-request form | [BigQuery guide](https://developers.google.com/weathernext/guides/bigquery) |
| DWD ICON | no (24 h retention) | none | [DWD](https://www.dwd.de/EN/ourservices/nwp_forecast_data/nwp_forecast_data.html) |
| GHCNh obs (36894, 36891, 36870, UAAA…) | yes (3-hourly SYNOP) | none | [GHCNh 36894](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year/2026/psv/GHCNh_KZM00036894_2026.psv) |
| ISD global-hourly | no (ends 2025) | none | [404 2026](https://www.ncei.noaa.gov/data/global-hourly/access/2026/36894099999.csv) |
| Meteostat bulk / Python | rows exist but 2026 = model (`metno_forecast`) | none (JSON API needs key) | [data.meteostat.net](https://data.meteostat.net/hourly/2026/36894.csv.gz) |
| Kazhydromet DB portal | 2000→present, monthly updates | registration | [meteo.kazhydromet.kz](https://meteo.kazhydromet.kz/database_meteo) |
| OGIMET / rp5 | likely | none, but bot-blocked (403) / manual export | [OGIMET](https://www.ogimet.com/cgi-bin/gsynres?ind=36894&ano=2026&mes=2&day=2&hora=0&ndays=2&lang=en) |
| GWA v4 GeoTIFF | static | none | [GWA API](https://globalwindatlas.info/api/gis/country/KAZ/wind-speed/100) |
| Copernicus DEM 30 m / ESA WorldCover | static | none | [DEM tile](https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N43_00_E078_00_DEM/Copernicus_DSM_COG_10_N43_00_E078_00_DEM.tif), [WorldCover tile](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N42E078_Map.tif) |

### Inferences
- To keep the evaluation reproducible offline, pre-extract point time series (site ± 1–2 grid cells) from the keyless archives into the repo (small CSV/Parquet), and keep the download scripts (keyless) for re-generation; respect CC-BY-4.0 attribution for ECMWF open data.
- Prefer GCS for ECMWF open data (AWS 503 SlowDown observed), and AWS/GCS for GFS; never rely on NOMADS/Azure/ECMWF-server for historical dates.

### Gaps
- Download throughput / total volume for a full Feb-2026 backtest with byte-range subsetting was not benchmarked.
- Licence terms of GHCNh (public domain for NOAA data is typical) and Meteostat (CC BY-NC 4.0 historically) not re-verified in 2026.
