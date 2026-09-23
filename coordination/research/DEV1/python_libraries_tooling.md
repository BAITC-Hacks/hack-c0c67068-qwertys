# Python libraries & developer tooling for a wind-power forecasting hackathon (Windows 11 + Python 3.12, state as of 2026-09-23)

How to read the evidence labels:
- **[PyPI]**: the PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`), queried 2026-09-23. It gives the latest version, upload date, `requires_python`, `requires_dist`, and whether a `win_amd64` / `cp312` wheel exists. Sizes are the compressed download size of the Windows cp312 wheel (or the pure wheel), not the installed size. Each claim links to the project page.
- **[dry-run]**: `pip 26.2.1 install --dry-run <pkg>`, run in the project venv (`repo\.venv`: CPython 3.12.10 NuGet build, pandas 3.0.6, numpy 2.5.3, scikit-learn 1.9.1, lightgbm 4.7.0). It shows exactly which packages pip *would* install, upgrade or downgrade. Nothing was installed.
- **[local]**: a Python snippet actually executed in that same venv on 2026-09-23.

---

## 1. Data stack: pandas 3.x breaking changes, polars, pyarrow, duckdb, xarray / GRIB / netCDF / zarr / fsspec

### Takeaway
pandas 3.0.6 is already installed and breaks a lot of older time-series code. Uppercase aliases (`'H'`, `'T'`, `'S'`, `'A'`, `'M'`, `'Y'`, `'Q'`) now **raise ValueError**. Datetimes default to **microsecond** resolution. Strings get the new `str` dtype. Chained assignment silently does nothing. `fillna(method=)` is gone. GRIB decoding on Windows is now pip-installable: the `eccodes` wheel for Windows bundles the C library, so `pip install eccodes cfgrib xarray` is enough and conda is not needed.

### Cited Findings
**pandas 3.0 (installed 3.0.6)**
- Version and wheel: pandas 3.0.6, uploaded 2026-09-17, needs Python >= 3.11. The cp312 win_amd64 wheel is 9.7 MB. — [PyPI](https://pypi.org/project/pandas/)
- Minimum dependencies are now Python 3.11, NumPy 1.26.0 and PyArrow 13.0.0 (PyArrow is optional). — [pandas 3.0.0 whatsnew](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
- **Copy-on-Write is always on.**
  - Any indexing result "behaves as a copy", so `df['A'][0] = 10` no longer modifies `df`.
  - `SettingWithCopyWarning` has been removed.
  - The `mode.copy_on_write` option is deprecated, has no effect, and goes away in 4.0.
  - — [whatsnew](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
  - Confirmed by test: `df["a"][0] = 99` leaves `df` unchanged and emits a `ChainedAssignmentError` warning. Use `df.loc[0, "a"] = 99`. — [local]
- **Default string dtype `str`.**
  - It is backed by PyArrow when installed, otherwise by NumPy object. It can hold only strings or NA.
  - Code that checks `dtype == object` breaks.
  - — [whatsnew](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
  - Confirmed by test: pyarrow is **not** installed in the venv. `pd.Series(["a","b"]).dtype` shows `str`, and `== object` returns `False`. — [local]
- **Datetime resolution is no longer always nanoseconds.**
  - Parsed strings default to `us`. `to_datetime(..., unit="s")` gives `datetime64[s]`. `date_range`/`timedelta_range` infer the unit.
  - `astype("int64")` now returns values 1000x smaller than before. Call `as_unit()` first.
  - — [whatsnew](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
  - Confirmed by test:
    - `pd.to_datetime(["2026-01-01 00:00"])` gives `datetime64[us]`.
    - With `utc=True` it gives `datetime64[us, UTC]`.
    - `pd.to_datetime([1767225600], unit="s", utc=True)` gives `datetime64[s, UTC]`. This is relevant because Open-Meteo returns unix seconds.
    - `date_range(freq="h").unit` is `us`.
    - `.asi8` returns 1767225600000000 (µs). `.as_unit("s").asi8` returns 1767225600.
    - — [local]
- **Frequency aliases.**
  - `M/Q/Y/BM/BQ/BY` have been removed; use `ME/QE/YE/BME/BQE/BYE`.
  - Lowercase `d`, `w`, `b` are deprecated.
  - `Timedelta` units `w, d, MIN, MS, US, NS` are deprecated.
  - — [whatsnew](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
  - Tested in pandas 3.0.6 with `pd.date_range(..., freq=X)`. — [local]
    - Raise `ValueError: Invalid frequency`: `'H'`, `'T'`, `'S'`, `'A'`, `'Y'`, `'M'`, `'Q'`, `'15T'`.
    - Work: `'h'`, `'min'`, `'s'`, `'D'`, `'ME'`, `'YE'`, `'QE'`, `'MS'`, `'15min'`.
    - `'d'` works but raises a deprecation FutureWarning.
- **Time zones.** pandas now uses `zoneinfo`/`datetime.timezone` instead of pytz. pytz is optional (`pip install pandas[timezone]`), and pytz exceptions are replaced by `ValueError`. — [whatsnew](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
  - Confirmed by test: a UTC index has `tz` of type `datetime.timezone`. The `tzdata` package is present in the venv and `ZoneInfo("Asia/Almaty")` resolves. — [local]
- **`pd.offsets.Day` is now a calendar day**, not 24 h. `Timedelta` no longer accepts `Day`, and `Day` no longer supports division. — [whatsnew](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
- **Other behaviour changes.** — [whatsnew](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
  - `inplace=True` methods (`fillna`, `ffill`, `interpolate`, `where`, `clip` …) now return `self` instead of `None`.
  - `concat(sort=False)` is now honoured for a DatetimeIndex.
  - `concat(ignore_index=True, keys=...)` raises.
  - NaN in nullable Float64 is now treated as NA.
  - `type(df)` prints `pandas.DataFrame`.
- **`fillna(method="ffill")` has been removed.** It raises `TypeError: ... unexpected keyword argument 'method'`. Use `.ffill()` / `.bfill()`. — [local]

**Other data libraries**
- **numpy** 2.5.3 needs Python >= 3.12; the win wheel is 12.6 MB. **scipy** 1.18.1 needs Python >= 3.12; the win wheel is 36.7 MB. — [PyPI numpy](https://pypi.org/project/numpy/), [PyPI scipy](https://pypi.org/project/scipy/)
- **polars** 1.44.2 (2026-09-09): `polars` is now a thin pure-Python meta-package (0.9 MB). It depends on `polars-runtime-32==1.44.2`, and extras `rt64` / `rtcompat` select other runtimes. — [PyPI](https://pypi.org/project/polars/)
- **pyarrow** 25.0.1 (2026-08-10) has a 28.0 MB cp312 win wheel. Streamlit excludes one version: `pyarrow!=25.0.0,<26`. — [PyPI pyarrow](https://pypi.org/project/pyarrow/), [PyPI streamlit](https://pypi.org/project/streamlit/)
- **duckdb** 1.5.5 (2026-07-22) has a 13.2 MB cp312 win wheel. — [PyPI](https://pypi.org/project/duckdb/)
- **xarray** 2026.7.0 is pure Python and needs Python >= 3.11. It installs cleanly in the pandas 3 venv. — [PyPI](https://pypi.org/project/xarray/), [dry-run]

**GRIB / netCDF / zarr / fsspec**
- **ecCodes Python (`eccodes`)**
  - Latest is 2.48.0 (2026-08-25), with a 7.6 MB cp312 win_amd64 wheel. — [PyPI](https://pypi.org/project/eccodes/)
  - From 2.43.0, Linux/macOS pull the binary library from the separate `eccodeslib` package. Quote: *"On Windows, the ecCodes Python bindings will continue to directly provide the ecCodes binary library without a dependency on eccodeslib."* — [PyPI eccodes](https://pypi.org/project/eccodes/)
  - Check the setup with `python -m eccodes selfcheck`.
  - To use an external library, set `ECCODES_PYTHON_USE_FINDLIBS=1`.
  - The conda alternative is `conda install -c conda-forge python-eccodes`.
  - — [PyPI eccodes](https://pypi.org/project/eccodes/)
- **eccodeslib** 2.49.0.30 (2026-09-22) ships only macOS and manylinux wheels, **no Windows**. Herbie therefore depends on `eccodeslib ... ; sys_platform != "win32"`. — [PyPI eccodeslib](https://pypi.org/project/eccodeslib/), [PyPI herbie-data](https://pypi.org/project/herbie-data/)
- **cfgrib** 0.9.15.1 (2025-09-30) is pure Python, "Beta", and requires `eccodes>=0.9.8`. — [PyPI](https://pypi.org/project/cfgrib/)
  - The dry-run pulls in `eccodes-2.48.0`, findlibs, cffi, attrs and click, with no conflicts. — [dry-run]
  - Historically, Windows support in ecCodes/cfgrib was "experimental" and needed a system ecCodes. — [cfgrib issue #22](https://github.com/ecmwf/cfgrib/issues/22)
- **ecmwflibs** 0.7.0 (Alpha) is the older ECMWF bundle; its win wheel is 47.8 MB. — [PyPI](https://pypi.org/project/ecmwflibs/)
- **netCDF4** 1.7.4 (2026-01-05) ships win_amd64 wheels (21.4 MB), though not with a cp312-specific tag. The pure-Python alternative is **h5netcdf** 1.8.1. — [PyPI netCDF4](https://pypi.org/project/netCDF4/), [PyPI h5netcdf](https://pypi.org/project/h5netcdf/)
- **zarr** 3.4.0 (2026-09-15) needs Python >= 3.12. — [PyPI](https://pypi.org/project/zarr/)
- **fsspec** and **s3fs** are both 2026.9.0 (2026-09-18) and pure Python. — [PyPI fsspec](https://pypi.org/project/fsspec/), [PyPI s3fs](https://pypi.org/project/s3fs/)

### Inferences
- **Code checklist for pandas 3:**
  - Use `freq="h"` / `"min"` / `"D"` / `"ME"`.
  - Write with `df.loc[mask, col] = v`, never chained.
  - Use `.ffill()` instead of `fillna(method=)`.
  - Test for strings with `pd.api.types.is_string_dtype(s)`, not `dtype == object`.
  - For integer epochs, write `idx.as_unit("s").asi8`, or `// 10**9` only after `as_unit("ns")`.
  - Always parse with `utc=True` and `tz_convert` only for display.
  - Avoid pytz (it is not installed).
- **`merge`/`merge_asof`** between frames whose datetime columns have different units (e.g. `[s, UTC]` from Open-Meteo vs `[us]` from CSV) is a likely source of subtle bugs. Normalise with `.dt.as_unit("us")` (or `"ns"`) on both sides before joining.
- **LightGBM and pandas 3 `str` columns.** LightGBM's pandas path accepts only int/float/bool/category. `str` columns (e.g. turbine_id) should be cast with `.astype("category")` before training.
- **Consider `pip install pyarrow`** (28 MB). It gives Parquet I/O (`df.to_parquet`), faster Arrow-backed `str`, and is required anyway by Streamlit and statsforecast.
- **For a 4-hour hackathon, pandas + pyarrow/Parquet is enough.** polars and duckdb add little at 2 turbines × hourly data (roughly 10^4–10^5 rows).
- **GRIB on Windows:** `pip install eccodes cfgrib xarray`, then `python -m eccodes selfcheck`. This should now work without conda, but it was not smoke-tested here. Only go to GRIB (GFS/ECMWF) if Open-Meteo is insufficient.
- **Keyless NOAA GFS access** is typically `s3fs.S3FileSystem(anon=True)` on the public `noaa-gfs-bdp-pds` bucket (the bucket name is from memory; verify). Herbie wraps this.

### Gaps
- The binary size of `polars-runtime-32` was not measured.
- `merge_asof` with mixed datetime resolutions was not tested.
- The Windows `eccodes`/`cfgrib` wheel was not installed/selfchecked on this machine (only dry-run resolution).
- The installed size on disk (vs wheel size) was not measured for any package.

---

## 2. Weather data clients and wind-domain libraries

### Takeaway
All the core weather clients are small, pure-Python, and resolve cleanly against pandas 3 / numpy 2.5 on Windows: openmeteo-requests, requests-cache, ecmwf-opendata, herbie-data, cfgrib, meteostat v2, metpy, windpowerlib and windrose. The two wind-analysis toolkits **OpenOA and brightwind pin `pandas<3`**. Installing either would downgrade pandas to 2.3.3, and OpenOA would also take scikit-learn down to 1.6.1. Keep them out of the main environment.

### Cited Findings
**Open-Meteo client**
- **openmeteo-requests** 1.7.5 (2026-01-19)
  - It now depends on **`niquests>=3.15.2`** (not requests) and `openmeteo-sdk>=1.22.0`. — [PyPI](https://pypi.org/project/openmeteo-requests/)
  - Its dependency tree adds niquests 3.21.2, urllib3-future, qh3, jh2, wassima and flatbuffers. — [dry-run]
- **openmeteo-sdk** 1.28.0 (2026-07-29) provides the FlatBuffers schema (`openmeteo_sdk.Variable`). — [PyPI](https://pypi.org/project/openmeteo-sdk/)
- **README usage pattern (still current):** — [open-meteo/python-requests README](https://github.com/open-meteo/python-requests)
  ```python
  import openmeteo_requests, requests_cache, pandas as pd
  from retry_requests import retry
  cache = requests_cache.CachedSession('.cache', expire_after=3600)
  om = openmeteo_requests.Client(session=retry(cache, retries=5, backoff_factor=0.2))
  r = om.weather_api("https://api.open-meteo.com/v1/forecast",
                     params={"latitude": 52.52, "longitude": 13.41, "hourly": ["wind_speed_10m", ...]})[0]
  h = r.Hourly()
  idx = pd.date_range(start=pd.to_datetime(h.Time(), unit="s", utc=True),
                      end=pd.to_datetime(h.TimeEnd(), unit="s", utc=True),
                      freq=pd.Timedelta(seconds=h.Interval()), inclusive="left")
  vals = h.Variables(0).ValuesAsNumpy()   # same order as the requested "hourly" list
  ```
  - The README does not mention an API key. The service is keyless for non-commercial use (verify the terms separately). — [README](https://github.com/open-meteo/python-requests)
- **requests-cache** 1.3.3 (2026-07-03) is maintained. **retry-requests** 2.0.0 had its last release on 2023-05-28 (stale but tiny). — [PyPI requests-cache](https://pypi.org/project/requests-cache/), [PyPI retry-requests](https://pypi.org/project/retry-requests/)

**NWP GRIB clients**
- **herbie-data** 2026.9.1 (2026-09-20), needs Python >= 3.11. — [PyPI](https://pypi.org/project/herbie-data/)
  - Dependencies: `eccodes>=2.45.0`, `eccodeslib` (non-Windows only), `pandas>=2.2.3`, `pyproj>=3.7`, `requests`, `xarray>=2025.1.1`. Extras: `extras`, `metpy`, `plot`, `pygrib`, `scikit-learn`. — [PyPI](https://pypi.org/project/herbie-data/)
  - The dry-run resolves with no downgrades: it adds cfgrib, eccodes-2.48.0, pyproj-3.8.0 and xarray. — [dry-run]
  - Install via `pip install herbie-data` / `'herbie-data[extras]'`, conda-forge, or `uv add herbie-data`. wgrib2 is optional (via pixi/conda). The docs have **no Windows-specific notes**. — [Herbie install docs](https://herbie.readthedocs.io/en/stable/user_guide/install.html)
- **ecmwf-opendata** 0.3.34 (2026-07-30) is pure Python with a single dependency (`multiurl`). The dry-run also adds pytz and tqdm. — [PyPI](https://pypi.org/project/ecmwf-opendata/), [dry-run]
  - Usage: `from ecmwf.opendata import Client; Client(source="aws").retrieve(type="fc", step=..., param=["100u","100v","10u","10v"], target="f.grib2")`. — [ecmwf-opendata README](https://github.com/ecmwf/ecmwf-opendata)
  - Sources: `"ecmwf"` (default, capped at 500 simultaneous connections), `"aws"`, `"google"`, `"azure"`.
  - Models: `ifs`, `aifs-single`, `aifs-ens`. Streams include `oper`, `enfo`, `wave`.
  - 0.25° grid. HRES steps are 0–144 h every 3 h, then every 6 h to 240 h.
  - Wind parameters are `10u/10v/100u/100v`.
  - Licence is **CC BY 4.0**.
- **cdsapi** 0.7.7 (2025-09-30, Beta). The newer **ecmwf-datastores-client** 0.5.3 (2026-07-31) is "Production/Stable". — [PyPI cdsapi](https://pypi.org/project/cdsapi/), [PyPI ecmwf-datastores-client](https://pypi.org/project/ecmwf-datastores-client/)

**Station observations**
- **meteostat** 2.1.5 (2026-09-17), needs Python >= 3.11 and `pandas>=2.3.0,<4.0.0`. Pandas 3 is fine. — [PyPI](https://pypi.org/project/meteostat/)
  - The dry-run also installs an old `pytz-2023.4`. — [dry-run]
  - v2 API:
    ```python
    import meteostat as ms
    p = ms.Point(lat, lon, elev)
    st = ms.stations.nearby(p, limit=4)
    ts = ms.hourly(st, start, end)
    df = ms.interpolate(ts, p).fetch()
    ```
    Also `ms.daily`, `ms.Parameter`. It uses bulk data with **no API key**, and the data is **CC BY 4.0**. — [meteostat GitHub](https://github.com/meteostat/meteostat)

**Physics and wind-domain libraries**
- **metpy** 1.7.1 (2025-08-29) pulls in Pint, pooch, pyproj and xarray. — [PyPI](https://pypi.org/project/metpy/), [dry-run]
- **pvlib** 0.15.2 has a 19.4 MB wheel and requires h5py. It is not needed for wind. — [PyPI](https://pypi.org/project/pvlib/), [dry-run]
- **windpowerlib** 0.2.2, last release **2024-02-20**, depends on `pandas` and `requests`. It installs with no downgrades. — [PyPI](https://pypi.org/project/windpowerlib/), [dry-run]
  - Features: power curves from the OEDB turbine library, log/Hellman hub-height extrapolation, barometric/ideal-gas air density, `ModelChain`, `TurbineClusterModelChain`, and wake losses. MIT licence.
  - Usage: `WindTurbine(turbine_type="E-126/4200", hub_height=135)`, then `ModelChain(turbine).run_model(weather_df)`. The weather DataFrame needs **MultiIndex columns** (variable, height).
  - Refreshing turbine data with `store_turbine_data_from_oedb()` needs internet.
  - — [windpowerlib GitHub](https://github.com/wind-python/windpowerlib)
- **OpenOA** 3.2 (2026-01-30, NREL): `requires_python >=3.10,<3.14`, **`pandas<3,>=2.2`, `scikit-learn<1.7,>=1.0`**, and bokeh. Its wheel is 54.2 MB. — [PyPI](https://pypi.org/project/openoa/)
  - The dry-run would **downgrade** pandas to 2.3.3, scikit-learn to 1.6.1 and scipy to 1.16.3. It would also add ipython, ipywidgets, bokeh 3.10, pygam, eia-python and shapely. — [dry-run]
- **brightwind** 2.7.0 (2026-05-14) pins **`pandas<3.0.0`**; its wheel is 32.8 MB. — [PyPI](https://pypi.org/project/brightwind/)
  - The dry-run downgrades pandas to 2.3.3 and pulls in pytest, ipython, gmaps, line_profiler, colormap and easydev as *runtime* deps. — [dry-run]
- **windrose** 1.10.0 (2026-04-10) depends only on matplotlib and numpy. — [PyPI](https://pypi.org/project/windrose/)

### Inferences
- **Recommended minimal weather stack:** `openmeteo-requests requests-cache retry-requests` (a few hundred kB). Add `meteostat` if station observations help.
- **GRIB (herbie-data / ecmwf-opendata + eccodes + cfgrib)** is only worth it if you need raw GFS/IFS at 100 m, or ensemble members, that Open-Meteo lacks.
- **Avoid for a reproducible README:** CDS/ERA5 via `cdsapi` needs a personal CDS token (`~/.cdsapirc`), which conflicts with the "no personal keys" requirement. Open-Meteo, ECMWF open data, NOAA GFS on AWS and Meteostat are all keyless.
- **Implement wind physics directly in numpy**, in ~10 lines, rather than pulling in libraries of uncertain pandas-3 compatibility:
  - Wind speed: `ws = np.hypot(u, v)`.
  - Direction: `wd = (270 - np.degrees(np.arctan2(v, u))) % 360`.
  - Shear extrapolation: `ws_hub = ws_ref * (h_hub/h_ref)**alpha` (alpha ≈ 0.14, or fitted from 10 m / 100 m).
  - Air density: `rho = p / (287.05 * T_K)`.
  - Density-corrected speed: `ws * (rho/1.225)**(1/3)`.
  - windpowerlib is optional, for a manufacturer power curve lookup.
- **Keep OpenOA and brightwind out of the main venv.** Use a separate venv if their filters or analysis are really needed.
- **Herbie typical call (from memory, verify):** `Herbie("2026-09-23 00:00", model="gfs", product="pgrb2.0p25", fxx=24).xarray(":[UV]GRD:100 m")`.

### Gaps
- windpowerlib 0.2.2 was not runtime-tested under pandas 3.0.6. Its last release predates pandas 3, so `freq` or chained-assignment issues are possible.
- It was not verified whether `retry_requests.retry()` (a `requests` session wrapper) is still fully compatible with the niquests-based `openmeteo_requests.Client` beyond the README example.
- The exact Open-Meteo hub-height variable names per endpoint (e.g. `wind_speed_80m/120m` in forecast vs `wind_speed_100m` in historical) were not verified here. That is left to the Open-Meteo researcher.
- Herbie and wgrib2 on native Windows were not smoke-tested.

---

## 3. ML / forecasting libraries: versions, weight, pandas-3 / numpy-2.5 / Windows compatibility

### Takeaway
The installed lightgbm and scikit-learn stack is the safest core. xgboost, catboost, statsmodels, optuna, shap, mapie, sktime and darts (without torch) all resolve cleanly with pandas 3.0.6 and numpy 2.5.3 on Windows. **The Nixtla stack (statsforecast, mlforecast, utilsforecast) and skforecast still pin `pandas<3`**, so installing them downgrades pandas to 2.3.3. neuralforecast and autogluon.timeseries pull in torch, Lightning, Ray or transformers (hundreds of MB), and AutoGluon caps `pandas<2.4` and `torch<2.11`.

### Cited Findings
**Compatibility matrix**

| pip name | latest (date) | Windows cp312 wheel | pandas-3 env result | Notes |
|---|---|---|---|---|
| lightgbm | 4.7.0 (2026-07-18) | `py3-none-win_amd64`, 1.4 MB | installed | — [PyPI](https://pypi.org/project/lightgbm/) |
| xgboost | 3.4.1 (2026-08-15) | win_amd64, **48.9 MB** | clean [dry-run] | needs **Python >= 3.12**; `nvidia-nccl-cu13` only on Linux — [PyPI](https://pypi.org/project/xgboost/) |
| catboost | 1.2.10 (2026-02-18) | cp312 win, **100.2 MB** | clean; adds plotly and graphviz [dry-run] | `pandas<4` — [PyPI](https://pypi.org/project/catboost/) |
| scikit-learn | 1.9.1 (2026-09-10) | 8.3 MB | installed | needs Python >= 3.11 — [PyPI](https://pypi.org/project/scikit-learn/) |
| statsmodels | 0.15.0 (2026-08-30) | 11.3 MB | clean; adds formulaic and patsy [dry-run] | — [PyPI](https://pypi.org/project/statsmodels/) |
| optuna | **5.0.0** (2026-09-07) | pure, 0.4 MB | clean; adds SQLAlchemy, alembic, colorlog [dry-run] | new major version — [PyPI](https://pypi.org/project/optuna/) |
| shap | 0.52.0 (2026-05-28) | cp312 win, 0.5 MB | clean; adds numba 0.67.0 and llvmlite 0.49 [dry-run] | needs Python >= 3.12 and numpy >= 2 — [PyPI](https://pypi.org/project/shap/) |
| MAPIE | 1.5.0 (2026-08-05) | pure | clean [dry-run] | — [PyPI](https://pypi.org/project/mapie/) |
| skforecast | 0.25.0 (2026-09-11) | pure | **downgrades pandas to 2.3.3** [dry-run] | `pandas<3.0,>=2.1`, numba, optuna — [PyPI](https://pypi.org/project/skforecast/) |
| sktime | 1.2.0 (2026-09-22) | pure, 8.2 MB | clean [dry-run] | `pandas<3.1`, `numpy<2.6`, `scikit-learn<1.10` — [PyPI](https://pypi.org/project/sktime/) |
| darts | 0.47.0 (2026-09-04) | pure | clean, but heavy [dry-run] | adds statsmodels, shap, numba, pyod, holidays, xarray; torch only via `darts[torch]` — [PyPI](https://pypi.org/project/darts/) |
| u8darts | 0.41.0 | — | — | classifier "Development Status :: 7 - **Inactive**"; use `darts` — [PyPI](https://pypi.org/project/u8darts/) |
| statsforecast | 2.1.1 (2026-07-16) | cp312 win, 0.6 MB | **downgrades pandas to 2.3.3** [dry-run] | `pandas<3.0.0`; adds fugue, triad, adagio, pyarrow, coreforecast — [PyPI](https://pypi.org/project/statsforecast/) |
| mlforecast | 1.1.0 (2026-07-10) | pure | **downgrades pandas to 2.3.3** [dry-run] | `pandas<3.0`; adds optuna, coreforecast, utilsforecast — [PyPI](https://pypi.org/project/mlforecast/) |
| utilsforecast | 0.2.16 (2026-04-27) | pure | pins `pandas<3.0.0` | Alpha — [PyPI](https://pypi.org/project/utilsforecast/) |
| neuralforecast | 3.2.2 (2026-09-08) | pure | pulls torch | `torch>=2.9.1`, `pytorch-lightning<2.6`, **`ray[train,tune]>=2.2`**, optuna — [PyPI](https://pypi.org/project/neuralforecast/) |
| autogluon.timeseries | 1.6.3 (2026-09-18) | pure (the deps are heavy) | would downgrade pandas | see the AutoGluon rows below — [PyPI](https://pypi.org/project/autogluon.timeseries/) |
| torch | 2.14.0 (2026-09-02) | cp312 win, **124.1 MB** | — | — [PyPI](https://pypi.org/project/torch/) |
| numba | 0.67.0 (2026-08-11) | cp312 win, 2.8 MB | — | `numpy<2.6,>=1.22`; numba 0.62.x capped `numpy<2.4` — [PyPI](https://pypi.org/project/numba/) |

**shap and darts on Windows.** Both declare `numba<0.63` **only** for `sys_platform == "darwin" and platform_machine == "x86_64"`. On Windows they take the latest numba (0.67), which supports numpy 2.5. — [PyPI shap](https://pypi.org/project/shap/), [PyPI darts](https://pypi.org/project/darts/)

**MAPIE v1 API**
- Classes: `SplitConformalRegressor`, `CrossConformalRegressor`, `JackknifeAfterBootstrapRegressor`, `ConformalizedQuantileRegressor`, and `TimeSeriesRegressor` (EnbPI/ACI).
- Workflow: `fit()` → `conformalize()` → `predict_interval()`, with a `confidence_level` argument.
- The v0.x classes `MapieRegressor` / `MapieTimeSeriesRegressor` and the `alpha` argument have been reworked, so old tutorials break.
- — [MAPIE docs](https://mapie.readthedocs.io/en/latest/)

**AutoGluon**
- **autogluon.timeseries** 1.6.3 requirements: `numpy<2.6`, `scipy<1.19`, **`pandas<2.4`**, **`torch<2.11,>=2.10`**, `lightning<2.7`, `transformers[sentencepiece]<5.15,>=5.3`, `accelerate`, `huggingface_hub[torch]`, `gluonts<0.18`, `chronos-forecasting<2.4`, `statsforecast<2.1.2`, `mlforecast<0.15`, `tensorboard`, and `autogluon.tabular[catboost,lightgbm,xgboost]==1.6.3`. — [PyPI](https://pypi.org/project/autogluon.timeseries/)
- Windows is supported on Python 3.10–3.13. The CPU install is `pip install autogluon.timeseries --extra-index-url https://download.pytorch.org/whl/cpu`. The docs recommend Anaconda on Windows and link a GitHub issue for Windows install trouble. — [AutoGluon install docs](https://auto.gluon.ai/stable/install.html)

**PyTorch**
- PyPI hosts **CPU-only** torch wheels for Windows and macOS. — [uv PyTorch guide](https://docs.astral.sh/uv/guides/integration/pytorch/)
- An explicit CPU index can be pinned with uv:
  ```toml
  [[tool.uv.index]]
  name="pytorch-cpu"
  url="https://download.pytorch.org/whl/cpu"
  explicit=true

  [tool.uv.sources]
  torch=[{index="pytorch-cpu"}]
  ```
  Or use `uv pip install torch --torch-backend=auto`. — [uv PyTorch guide](https://docs.astral.sh/uv/guides/integration/pytorch/)

### Inferences
- **Hackathon default:**
  - Model: `lightgbm` (installed).
  - Quantile models: `LGBMRegressor(objective="quantile", alpha=q)` for P10/P50/P90, or sklearn `HistGradientBoostingRegressor(loss="quantile")`.
  - Monotonic clipping to [0, rated power].
  - Isotonic calibration via sklearn `IsotonicRegression` if needed.
  - Optionally MAPIE `SplitConformalRegressor` for intervals.
  - Optionally optuna (small, clean) and shap (clean) for explainability slides.
  - This adds under 2 MB of wheels beyond what is already installed.
- **Nixtla (mlforecast/statsforecast) and skforecast** are worthwhile only if you also pin `pandas==2.3.3` for the whole project. That is a legitimate choice, but it must be decided up-front, because the code must then avoid pandas-3-only behaviour and vice versa. With ~4 h left and pandas 3 already in use, direct LightGBM with hand-made lag/lead features is lower risk.
- **Too heavy or risky for 4 h on Windows:** autogluon.timeseries (torch + transformers + Lightning + gluonts, several hundred MB to GB installed, pandas downgrade), neuralforecast (torch + Ray), and darts[torch].
  - For a "foundation-model" baseline, a single Chronos checkpoint is possible but out of scope here.
- **catboost's 100 MB wheel** is acceptable but offers little benefit over LightGBM at this data size.
- **xgboost 3.4.x needs Python >= 3.12.** It is fine here, but pin it if reviewers may use 3.11.

### Gaps
- Ray on Windows / Python 3.12 (a neuralforecast dependency) was not checked.
- The torch installed footprint on Windows was not measured.
- There was no runtime test of sktime/darts with the pandas 3 `str` dtype or `us` resolution. Dependency resolution is clean, but runtime behaviour is unverified.
- The AutoGluon docs give no install-size figure.

---

## 4. Evaluation and visualisation (CRPS, plotting, report generation)

### Takeaway
For CRPS and quantile scores use **scoringrules** (maintained, needs Python >= 3.12 and numpy >= 2). **properscoring** has not been released since 2015. matplotlib works, but this NuGet Python build has **no tkinter**, so plots are file-only (Agg backend). Plotly static export needs Kaleido v1 **plus a local Chrome**.

### Cited Findings
**Scoring**
- **properscoring** 0.1 was last released **2015-11-12** (Alpha). — [PyPI](https://pypi.org/project/properscoring/)
- **scoringrules** 0.11.0 (2026-06-06) needs Python >= 3.12, `numpy>=2.0` and `scipy>=1.14`. Extras: `jax`, `numba`, `torch`. — [PyPI](https://pypi.org/project/scoringrules/)
  - Scores: CRPS (`sr.crps_ensemble(obs, fct)`), threshold-weighted CRPS, energy and variogram scores, Brier, log score, RPS, Dawid–Sebastiani.
  - Backends: numpy (numba-accelerated), jax, pytorch.
  - — [scoringrules GitHub](https://github.com/frazane/scoringrules)

**Plotting**
- **matplotlib** 3.11.2 (2026-09-11) has a 9.3 MB cp312 win wheel. — [PyPI](https://pypi.org/project/matplotlib/)
  - This venv's base Python (NuGet build, `C:\Users\user\AppData\Local\Programs\Python312`) has **no `tkinter`** (`ModuleNotFoundError`). matplotlib therefore reports backend `agg`: `plt.show()` opens no window, so use `savefig`. — [local]
- **plotly** 7.1.0 (2026-09-15) has a 9.7 MB wheel. **kaleido** 1.4.0 (2026-08-31). — [PyPI plotly](https://pypi.org/project/plotly/), [PyPI kaleido](https://pypi.org/project/kaleido/)
  - Kaleido v1 *"looks for a compatible version of Chrome (or Chromium) already installed"*. Install Chrome via the `plotly_get_chrome` command or `plotly.io.get_chrome()`. — [Plotly static image export](https://plotly.com/python/static-image-export/)
- **altair** 6.3.0 (needs Python >= 3.11). **vl-convert-python** 1.9.0.post1 has a 32.1 MB win wheel for PNG/SVG export. — [PyPI altair](https://pypi.org/project/altair/), [PyPI vl-convert-python](https://pypi.org/project/vl-convert-python/)
- **seaborn** 0.13.2 was last released 2024-01-25; it is slow-moving but still works. — [PyPI](https://pypi.org/project/seaborn/)

**Reports and notebooks**
- **jinja2** 3.1.6 (2025-03-05). — [PyPI](https://pypi.org/project/jinja2/)
- **nbconvert** 7.17.1 (2026-04-08). — [PyPI](https://pypi.org/project/nbconvert/)
- **papermill** 2.7.0 (2026-02-27, needs Python >= 3.10, 103 requirement entries including extras). — [PyPI](https://pypi.org/project/papermill/)
- **jupyterlab** 4.6.4 (2026-09-21) has a 17.2 MB wheel. — [PyPI](https://pypi.org/project/jupyterlab/)
- **quarto-cli** 1.10.18 is on PyPI (2026-07-24). The probe found no Windows wheel and no pure wheel in the latest release's file list. — [PyPI](https://pypi.org/project/quarto-cli/)

### Inferences
- **Metrics.** Implement MAE, RMSE and nMAE (normalised by rated power) in numpy. For quantile forecasts, pinball loss is 3 lines. Use `scoringrules.crps_ensemble`, or compute CRPS from quantiles as the average pinball loss × 2. Skip properscoring.
- **Demo visuals.** Use matplotlib PNGs, which are robust with no GUI needed, for README/CI. Use plotly for an interactive dashboard (Streamlit or Gradio render it natively). Avoid static plotly export (Chrome dependency) in reproducible scripts.
- **Reports.** A Jinja2 → HTML or Markdown report generated by the pipeline is the lightest option. Quarto needs a separate binary install (~100+ MB). Papermill and nbconvert add Jupyter dependencies. Neither is worth it within 4 h.

### Gaps
- The quarto-cli PyPI install mechanism on Windows was not verified. It may be a platform wheel under a different tag, or an sdist that downloads the binary.
- The scoringrules `crps_quantile` / quantile-based function names were not confirmed from the docs.

---

## 5. Serving, UI, CLI, scheduling / orchestration, config, logging

### Takeaway
Everything in the UI and CLI tier is pure Python with Windows-friendly wheels. **Streamlit 1.64** is the quickest dashboard: it now bundles uvicorn and starlette, and it pulls pyarrow and altair. FastAPI and uvicorn are small. Gradio and Panel are ~30 MB each. For scheduling, APScheduler 3.11 or `schedule` suffice. Prefect 3 and Dagster are heavy (FastAPI, SQLAlchemy, gRPC). **Airflow does not run natively on Windows** (WSL2 or containers only).

### Cited Findings
**Serving and UI**
- **fastapi** 0.141.1 (2026-07-29) and **uvicorn** 0.53.0 (2026-09-14) are pure Python and ~0.1 MB each. — [PyPI fastapi](https://pypi.org/project/fastapi/), [PyPI uvicorn](https://pypi.org/project/uvicorn/)
- **streamlit** 1.64.0 (2026-09-15) has a 10.1 MB wheel. — [PyPI](https://pypi.org/project/streamlit/)
  - Requirements include `altair<7`, `pandas<4`, `protobuf<8,>=5.26.1`, `pyarrow!=25.0.0,<26,>=7.0` and `uvicorn<1,>=0.30.0`. — [PyPI](https://pypi.org/project/streamlit/)
  - The dry-run adds pyarrow-25.0.1, altair-6.3.0, protobuf-7.36.2, pydeck, starlette-1.7.0, uvicorn-0.53.0, watchdog-6.0.0 and websockets. — [dry-run]
- **gradio** 6.28.0 (2026-09-18) has a 31.4 MB wheel and requires fastapi, `huggingface-hub<2.0,>=1.16.0` and uvicorn. — [PyPI](https://pypi.org/project/gradio/)
- **panel** 1.9.4 (30.3 MB) requires `bokeh<3.10.0,>=3.7.0` and param. — [PyPI](https://pypi.org/project/panel/)
- **dash** 4.4.1 (8.9 MB) requires plotly. — [PyPI](https://pypi.org/project/dash/)
- **nicegui** 3.17.1 (8.6 MB) requires fastapi and `uvicorn[standard]`. — [PyPI](https://pypi.org/project/nicegui/)

**CLI**
- **typer** 0.27.2, **click** 8.5.0 and **rich** 15.0.0 are all pure Python. — [PyPI typer](https://pypi.org/project/typer/), [PyPI click](https://pypi.org/project/click/), [PyPI rich](https://pypi.org/project/rich/)

**Scheduling and orchestration**
- **APScheduler**: the latest stable on PyPI is **3.11.3** (2026-06-28). The 4.x line is not the default release. — [PyPI](https://pypi.org/project/apscheduler/)
- **schedule** 1.2.2, last released 2024-06-18. — [PyPI](https://pypi.org/project/schedule/)
- **watchdog** 6.0.0 (2024-11-01) has Windows wheels. — [PyPI](https://pypi.org/project/watchdog/)
- **prefect** 3.8.6 (2026-09-15) has a 15.7 MB wheel. — [PyPI](https://pypi.org/project/prefect/)
  - Core deps: `fastapi<1.0.0,>=0.139.0`, `sqlalchemy[asyncio]`, pydantic, pydantic-settings, `httpx[http2]`, uvicorn, cloudpickle, and pendulum (Python < 3.13).
- **dagster** 1.13.24 (2026-09-21) requires grpcio, grpcio-health-checking, `protobuf<7` and SQLAlchemy. — [PyPI](https://pypi.org/project/dagster/)
- **apache-airflow** 3.3.2 (2026-09-17) has 251 requirement entries (mostly extras). — [PyPI](https://pypi.org/project/apache-airflow/)
  - It runs on POSIX systems; on Windows only via **WSL2 or Linux containers**. — [apache-airflow PyPI / docs as summarised](https://pypi.org/project/apache-airflow/), [coder2j guide](https://coder2j.com/airflow-tutorial/install-airflow-on-windows/)

**Config**
- **pydantic** 2.13.5, **pydantic-settings** 2.15.0 and **python-dotenv** 1.2.3 are small and pure. — [PyPI pydantic-settings](https://pypi.org/project/pydantic-settings/), [PyPI python-dotenv](https://pypi.org/project/python-dotenv/)
- **hydra-core** 1.3.7 (2026-09-14). Its classifiers only list Python 3.10/3.11. — [PyPI](https://pypi.org/project/hydra-core/)

**Logging**
- **loguru** 0.7.3, last released 2024-12-06. — [PyPI](https://pypi.org/project/loguru/)
- **structlog** 26.1.0 (2026-06-06). — [PyPI](https://pypi.org/project/structlog/)

### Inferences
- **Demo UI.** Streamlit is the fastest route to "forecast chart + table + button to re-run the agent pipeline" (`streamlit run app.py`). If a REST API is required, use FastAPI with `uvicorn app:app --port 8000`. Gradio fits if you want a chat-style box for the "agentic" layer.
- **Streamlit's `watchdog` pitfall.** Streamlit's file watcher on Windows can reload the app when the pipeline writes files into the repo. Write outputs outside the watched folder, or set `server.fileWatcherType = "none"` in `.streamlit/config.toml`.
- **Scheduling.** For the hackathon, "scheduling" should be a CLI command (`python -m windfc run --horizon 48`) plus an optional APScheduler `BlockingScheduler` with a cron trigger (e.g. hourly after new NWP runs). Prefect, Dagster and Airflow cost more setup time than they return in 4 h, and Airflow requires WSL2.
- **Config.** pydantic-settings with a `.env` file (and a committed `.env.example`) gives typed config and env-var overrides with no personal keys. Hydra is overkill.
- **Logging.** Standard `logging`, or loguru for a one-liner, is enough. Rich makes a nice console for the demo.

### Gaps
- Prefect 3 and Dagster native-Windows quirks (e.g. Prefect's local server on Windows) were not checked.
- The APScheduler 4.x pre-release status was not verified beyond "PyPI latest = 3.11.3".

---

## 6. Packaging and reproducibility (uv, pip-tools, poetry, task runners, Docker, CI, linting, templates, DVC)

### Takeaway
**uv** 0.12.18 is the current fast default: a single binary, a `uv.lock`, `uv run`, and CPU-torch index pinning. It installs on Windows with one PowerShell line, and it can export `requirements.txt` for pip-only reviewers. `make` is not native on Windows. `just` is pip-installable as `rust-just`, or you can ship a `run.ps1`. Docker Desktop needs WSL2 plus virtualization, and is paid for large companies. DVC and Cookiecutter scaffolding are overhead for a 4-hour build. The Papers-with-Code **ML Code Completeness Checklist** is the right mental model for the README.

### Cited Findings
**Environment and dependency tools**
- **uv** 0.12.18 (2026-09-22) is also on PyPI (18 MB win wheel). — [PyPI](https://pypi.org/project/uv/)
  - Windows install, any of:
    - `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` (a version-pinned URL also exists: `.../uv/0.12.18/install.ps1`)
    - `winget install --id=astral-sh.uv -e`
    - `pip install uv` / `pipx install uv`
  - Update with `uv self update`.
  - — [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/)
  - uv is **not on PATH** on this machine yet. The venv has pip 26.2.1. — [local]
- **pip-tools** 7.6.1 (2026-08-12). **poetry** 2.5.1 (2026-09-20). — [PyPI pip-tools](https://pypi.org/project/pip-tools/), [PyPI poetry](https://pypi.org/project/poetry/)

**Task runners** — [PyPI rust-just](https://pypi.org/project/rust-just/), [PyPI invoke](https://pypi.org/project/invoke/), [PyPI taskipy](https://pypi.org/project/taskipy/), [PyPI poethepoet](https://pypi.org/project/poethepoet/)
- **rust-just** 1.58.0 ships a win_amd64 binary wheel (2.4 MB) that provides `just`.
- **invoke** 3.0.3.
- **taskipy** 1.14.1, last released 2024-11-26.
- **poethepoet** 0.48.0.

**Code quality and testing** — [PyPI ruff](https://pypi.org/project/ruff/), [PyPI pre-commit](https://pypi.org/project/pre-commit/), [PyPI pytest](https://pypi.org/project/pytest/), [PyPI mypy](https://pypi.org/project/mypy/)
- **ruff** 0.16.8 (native binary wheel, 10.6 MB).
- **black** 26.5.1.
- **mypy** 2.3.1 (11.2 MB win wheel).
- **pytest** 9.1.1.
- **pre-commit** 4.6.2.

**Data versioning**
- **dvc** 3.67.1 (2026-03-31) has 82 requirement entries (including extras). — [PyPI](https://pypi.org/project/dvc/)

**Docker Desktop on Windows 11**
- Requirements: Windows 11 Enterprise/Pro/Education 23H2 (build 22631+), **WSL >= 2.1.5**, SLAT CPU, 8 GB RAM, and virtualization enabled in BIOS. Per-user install needs no admin rights.
- Licensing: paid subscription required for companies with >250 employees **or** >$10 M revenue.
- — [Docker docs](https://docs.docker.com/desktop/setup/install/windows-install/)
- This machine is Windows 11 Pro build 22631. — [local environment info]

**Project templates and README checklists**
- **Cookiecutter Data Science v2**: `pipx install cookiecutter-data-science`, then `ccds`. — [CCDS docs](https://cookiecutter-data-science.drivendata.org/)
  - Options: environment manager (including **uv**, conda, poetry, pixi), dependency file (requirements.txt / pyproject.toml / environment.yml), pytest, ruff, licence, mkdocs.
  - It generates `data/{raw,interim,processed,external}`, `models/`, `notebooks/`, `reports/figures`, `pyproject.toml`, a `Makefile`, and a module with `config.py`, `dataset.py`, `features.py`, `modeling/` and `plots.py`.
  - The docs have no Windows notes.
- **cookiecutter** 2.7.1. — [PyPI](https://pypi.org/project/cookiecutter/)
- **Papers with Code "ML Code Completeness Checklist"** has five items, plus a README.md template. — [releasing-research-code](https://github.com/paperswithcode/releasing-research-code), [Medium post](https://medium.com/paperswithcode/ml-code-completeness-checklist-e9127b168501)
  - The items: dependency specification, training code, evaluation code, pre-trained models, and a README with a results table plus the precise commands to reproduce them.
  - NeurIPS 2019 repos with all five items had the most stars (median 196).

### Inferences
- **Recommended for the 4-hour hackathon (Windows):**
  1. Keep the existing venv.
  2. Pin versions with `pip freeze > requirements.txt` (or hand-curated `==` pins).
  3. Optionally add `uv` and generate `uv.lock` / `pyproject.toml`, so experts can run `uv sync && uv run python -m windfc ...`. Also export `uv export --format requirements-txt > requirements.txt` for pip users. (The commands are from the uv docs structure; verify the flags.)
  4. Provide both a `run.ps1` (Windows) and a `Makefile` or `justfile` (Linux/macOS reviewers).
  5. Document `python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt`, plus the PowerShell execution-policy note (`Set-ExecutionPolicy -Scope Process Bypass`).
- **Pin `python_requires >=3.12`** in README/pyproject. numpy 2.5, scipy 1.18, xgboost 3.4, shap 0.52, scoringrules and zarr 3.4 all need Python >= 3.12.
- **Docker, devcontainers and DVC are optional nice-to-haves.** A Dockerfile (`python:3.12-slim` + `pip install -r requirements.txt`) takes ~10 minutes to write and is a good reproducibility signal for Linux experts, but don't debug Docker Desktop/WSL during the hackathon. DVC is unnecessary. Commit small sample data plus a download script instead.
- **CI.** A GitHub Actions workflow on `ubuntu-latest` (optionally `windows-latest`) runs `pip install -r requirements.txt && pytest -q` plus an offline smoke run on cached sample data. That proves reproducibility cheaply. ruff and pre-commit are optional.
- **Jupyter vs scripts.** Use scripts or modules plus a CLI as the reproducible path, with at most one notebook for EDA/demo. Papermill is not needed.
- **README skeleton** (from the PwC checklist):
  - Requirements / install
  - Data (sources, licences: Open-Meteo, ECMWF CC BY 4.0, Meteostat CC BY 4.0)
  - Training command
  - Evaluation command plus a results table (MAE/nMAE by horizon)
  - Forecast/run command
  - Env vars (`.env.example`, no personal keys)
  - Project structure
  - Known limitations

### Gaps
- The uv project-workflow pages (`uv init/add/lock/sync/run/export`) were not fetched in this session. Command names are standard, but flags should be verified at docs.astral.sh/uv.
- The "Made With ML" (madewithml.com) guidance was not fetched.
- No GitHub Actions or devcontainer docs were fetched.

---

## 7. LLM / agent client libraries (brief)

### Takeaway
The official **openai** (3.19.0) and **anthropic** (1.8.0) SDKs are small, pure Python, and released within the last few days. Both now depend on a package named **`httpx2`**. **ollama** 0.6.2 is the thin client for local models. **litellm** 1.102.1 is a unified API, but it is heavy (27 MB compiled win wheel) and had a **PyPI supply-chain compromise in March 2026**. Pin exact versions.

### Cited Findings
- **openai** 3.19.0 (uploaded 2026-09-23) requires `httpx2<3,>=2.12.0` and pydantic. — [PyPI](https://pypi.org/project/openai/)
- **anthropic** 1.8.0 (2026-09-22) requires `httpx2<3,>=2.0.0` and pydantic. Extras include `bedrock`, `vertex`, `mcp`. — [PyPI](https://pypi.org/project/anthropic/)
- **ollama** 0.6.2 (2026-04-29) requires `httpx>=0.27` and `pydantic>=2.9`. — [PyPI](https://pypi.org/project/ollama/)
- **httpx** 0.28.1 was last released 2024-12-06. — [PyPI](https://pypi.org/project/httpx/)
- **litellm** 1.102.1 (2026-09-23) now ships platform wheels, including win_amd64 (27.4 MB). — [PyPI](https://pypi.org/project/litellm/)
  - Core deps: `httpx<1.0,>=0.28`, `pydantic<3`, `pydantic-settings>=2.14.1`. Extras include `proxy`, `mcp`, `caching`.
- **The litellm compromise**: versions **1.82.7 and 1.82.8** were malicious. They were live on 2026-03-24 for about 40 minutes and were attributed to the TeamPCP campaign. — [LiteLLM security update](https://docs.litellm.ai/blog/security-update-march-2026), [Datadog Security Labs](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/)
  - A `litellm_init.pth` file ran on every Python start and harvested credentials.
  - Affected users should uninstall and rotate their credentials.

### Inferences
- **Choose one provider SDK** (or ollama for fully local and keyless) behind a tiny adapter. Keys are read from env vars (`OPENAI_API_KEY` / `ANTHROPIC_API_KEY`) via pydantic-settings or `.env`, never committed.
- **Make the agent layer degrade gracefully.** With no key set, the pipeline should run with a deterministic rule-based "agent" so experts can reproduce the forecast without personal keys.
- **If using litellm**, pin an exact version (never 1.82.7/1.82.8) and prefer hashes (`pip install --require-hashes` or `uv.lock`). Its footprint (27 MB wheel, many extras) is unnecessary if you target a single provider.

### Gaps
- What `httpx2` is (a fork or major rename of httpx) and its Windows behaviour were not investigated.
- Agent frameworks are covered by another researcher.
