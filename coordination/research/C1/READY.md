# C1 READY: SCADA and weather input sample

Status: implemented in C1 branch, UTC times are RFC3339 `Z`; source files and raw weather responses stay local in ignored `artifacts/` and `data/cache/`. There is **no February SCADA actual**. This package does not claim historical forecast accuracy.

## Contract for C2/C4

- `src.data.scada.prepare_hourly(path, turbine_id, utc_offset_hours=6, start_utc=None, end_utc=None)` returns hourly Observation dictionaries and a source report. `turbine_id` is `turbine_1` or `turbine_2`; `timestamp` UTC; `wind_m_s`, `temperature_c`, `power_normalized` are means of **unique** readings on the 10-minute grid. `coverage` is unique slots / 6. `quality_flags` includes `partial_hour`, `duplicate_timestamp`, `off_grid_timestamp`. Missing hours have no row. `timezone_status=inferred` and `utc_offset_hours=6` make the unresolved fixed-clock hypothesis explicit.
- `src.weather.open_meteo.probe(lat, lon, run, cache_dir, forecast_hours=72)` returns WeatherForecast dictionaries, report, cache path. `inspect_payload(payload, url, run)` replays offline. `select_horizon(rows, issue_time, 24|48)` requires each valid hour and rejects a run with inferred `available_at > issue_time`, missing hours or null variables. Fields include `run_time`, `valid_time`, `available_at`, `availability_basis=inferred_run_plus_6h`, `provenance_status=unconfirmed`, `variables`, `units`, `source_reference` SHA.
- Open-Meteo Single Runs `run` means initialization; `+6h` is a conservative **assumption**, not verified publication time. The archived response is observed now, but whether its exact fields were operationally published at the historical issue time remains unresolved. Keep cached/replay mode marked in API/UI. Stop calling the historical simulation leak-free until provenance is settled.

## Verified local run

Run from repository root with Python 3.10+ and the official CSVs at `D:\HACKALEM\cases`:

```powershell
python -m unittest discover -s tests -v
python -m src.data.scada --input 'D:\HACKALEM\cases\Dataset HackAlemAI для участников 11.03.2023-28.02.2026 - turbine 1.csv' --turbine-id turbine_1 --utc-offset-hours 6 --start-utc 2026-01-30T18:00Z --end-utc 2026-01-30T21:00Z --output artifacts/c1/scada-t1-sample.jsonl --report artifacts/c1/scada-t1-report.json
python -m src.weather.open_meteo --latitude 43.645150 --longitude 78.535604 --run 2026-01-31T00:00Z --forecast-hours 72 --cache-dir data/cache/weather --report artifacts/c1/weather-20260131-report.json
python -m src.weather.open_meteo --latitude 43.645150 --longitude 78.535604 --run 2026-01-31T00:00Z --forecast-hours 72 --cached-response data/cache/weather/3c846b4f520d1ee3f1cefa0d4be765c7cd12a41a077d026e18d083867871237e.json --issue-time 2026-01-31T07:00Z --horizon-hours 48 --report artifacts/c1/weather-replay-report.json --output artifacts/c1/weather-replay-48h.jsonl
```

The second command created **3 real hourly Observation rows** with coverage 1. The fourth created **48 real NWP rows** for valid times 2026-01-31 08:00Z through 2026-02-02 07:00Z. These data files are local and ignored by Git; their machine-readable reports are in this folder. An offline replay needs the cached response on the same machine. `source_reference` and `response_sha256` identify the exact bytes.

Full local preparation of both supplied CSVs under the same offset gave turbine_1: 142,360 source rows → 23,763 hourly rows (23,667 complete, 96 partial); turbine_2: 149,499 → 25,004 hourly rows (24,785 complete, 219 partial). Result files: `artifacts/c1/scada-t1-hourly.jsonl`, `artifacts/c1/scada-t2-hourly.jsonl`, not committed. Timestamps range 2023-03-10 18:00Z–2026-01-31 17:00Z under UTC+6 hypothesis. Missing hours are absent rather than filled. Source SHA256 values match `coordination/DATA_MANIFEST.json`.

Three small local weather response caches total 7,923 bytes, runs 2026-01-31/02-15/02-28 00Z, all 72 hourly records, no nulls for wind speed 100 m, wind direction 100 m, temperature 2 m. All snap to Open-Meteo grid 43.620384, 78.47891. Cache payloads are not committed; three report JSONs are. This checks API coverage/format, **not** as-issued provenance.

## Remaining gates

1. Obtain source metadata proving as-issued availability or label the historical weather path conditional. `available_at` must not be called an observed release timestamp.
2. Resolve SCADA timezone from owner metadata or perform sensitivity UTC+5/+6/+7 on pre-February data; UTC+6 remains inferred.
3. Agree with C2 how to use partial hours and normalize target; no February actuals or January rows after a simulated issue time may enter model features.
