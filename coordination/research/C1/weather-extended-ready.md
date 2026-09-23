# C1 V2 seasonal weather archive (separate from v1)

Requested by C2 as a fixed post-test experiment for seasonal stability. Dates: 2024-11-01..2025-10-31, one ECMWF IFS Single Runs 00Z initialization per day, issue12Z, 48 hourly fields after issue. This batch is under artifacts/c1/weather_extended and data/cache/weather_extended; the accepted v1 archive and its frozen January result are unchanged.

| Range | Expected runs | Ready | Selected hours | Raw bytes | Failed |
|---|---:|---:|---:|---:|---:|
| 2024-11-01..2025-02-28 | 120 | 120 | 5,760 | 320,955 | 0 |
| 2025-03-01..2025-06-30 | 122 | 122 | 5,856 | 329,273 | 0 |
| 2025-07-01..2025-10-31 | 123 | 118 | 5,664 | 319,181 | 5 |
| Total | 365 | 360 | 17,280 | 969,409 | 5 |

Local paths on laptop 1:

- D:\HACKALEM\worktrees\c1-data\artifacts\c1\weather_extended\manifest.json
- D:\HACKALEM\worktrees\c1-data\artifacts\c1\weather_extended\runs\YYYY-MM-DD.jsonl
- D:\HACKALEM\worktrees\c1-data\data\cache\weather_extended\SHA256.json

The [metadata manifest](weather-extended-manifest.json) is updated atomically after each day, with source URL, run/issue/valid times, SHA256, cache/rows path, grid point, null/missing counts, units, attribution, inferred availability and model cycle regime. It is committed for audit; raw responses and selected JSONL remain in ignored local directories. Reproduce from repository root:

```powershell
python -m src.weather.batch_archive --start-date 2024-11-01 --end-date 2025-02-28 --cache-dir data/cache/weather_extended --output-dir artifacts/c1/weather_extended/runs --manifest artifacts/c1/weather_extended/manifest.json --sleep-seconds 1
python -m src.weather.batch_archive --start-date 2025-03-01 --end-date 2025-06-30 --cache-dir data/cache/weather_extended --output-dir artifacts/c1/weather_extended/runs --manifest artifacts/c1/weather_extended/manifest.json --sleep-seconds 1
python -m src.weather.batch_archive --start-date 2025-07-01 --end-date 2025-10-31 --cache-dir data/cache/weather_extended --output-dir artifacts/c1/weather_extended/runs --manifest artifacts/c1/weather_extended/manifest.json --sleep-seconds 1
python -m src.weather.verify_archive --manifest artifacts/c1/weather_extended/manifest.json --start-date 2024-11-01 --end-date 2025-10-31
```

Stopped at the 15:08 timebox after attempting all 365 dates. The verifier reports 360/365 and exits nonzero **because exactly five source dates failed**; each of the other 360 passed SHA, 48-hour coverage, finite values and time gate. Missing: 2025-08-05, 08-06, 08-08 and 08-09 returned HTTP 400 after bounded retries; 2025-08-07 returned a nonfinite required variable at first selected hour. No invented fill was applied. The usable operational-epoch subset is 349 runs after also excluding the 11 early hindcasts. C2 can use the manifest status field to skip these issues.

**Training boundary:** [ECMWF model change record](https://www.ecmwf.int/en/forecasts/documentation-and-support/changes-ecmwf-model) places IFS Cycle 49r1 operational start on 2024-11-12. [Open-Meteo Single Runs docs](https://open-meteo.com/en/docs/single-runs-api) label earlier archive records as 49r1 hindcasts. Thus the 11 runs 2024-11-01..11 are tagged hindcast_pre_operational_49r1 and should be excluded from the core V2 as-issued training subset. The remaining 354 runs lie in the operational-cycle epoch but still have provenance_status=unconfirmed: no per-run historical publication time is provided. available_at=run+9h is an explicit assumption, not proof. This V2 archive is a fixed post-test experiment and must not revise the accepted v1.

Source attribution: [Open-Meteo Single Runs](https://open-meteo.com/en/docs/single-runs-api), underlying ECMWF IFS; [terms](https://open-meteo.com/en/terms) specify CC BY 4.0 and free non-commercial API use.
