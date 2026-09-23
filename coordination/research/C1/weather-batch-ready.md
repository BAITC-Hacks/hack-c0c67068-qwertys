# C1 weather batch for C2 (2025-11-01..2026-02-27)

Requested by C2 for training, frozen January holdout and February replay. Generated 23.09.2026 with the free Open-Meteo Single Runs API: one ECMWF IFS run initialized at 00:00Z per day, issue at 12:00Z, 48 valid hours after issue. Both turbines share one Open-Meteo grid cell. Weather variables: 100 m wind speed (m/s), 100 m wind direction (degrees), 2 m temperature (°C).

| Partition | Runs | Selected hours | Raw response bytes | Failed / null / missing |
|---|---:|---:|---:|---:|
| Train/validation, 2025-11-01..12-31 | 61 | 2,928 | 162,078 | 0 |
| Frozen holdout, 2026-01-01..01-30 | 30 | 1,440 | 80,370 | 0 |
| February replay inputs, 2026-01-31..02-27 | 28 | 1,344 | 74,481 | 0 |
| Total | 119 | 5,712 | 316,929 | 0 |

Local files on laptop 1:

- Index: D:\HACKALEM\worktrees\c1-data\artifacts\c1\weather-batch-manifest.json
- One 48-line JSONL per run: D:\HACKALEM\worktrees\c1-data\artifacts\c1\weather_runs\YYYY-MM-DD.jsonl
- Raw 72-hour responses by SHA256: D:\HACKALEM\worktrees\c1-data\data\cache\weather\SHA256.json

These payload/JSONL files are intentionally ignored by Git. The [committed metadata manifest](weather-batch-manifest.json) records source URL, run/issue/valid times, assumed availability, SHA, size, units, coverage, missing/null counts, license, attribution and relative local paths. For the other laptop or a fresh clone, run the following from repository root to recreate the local files:

```powershell
python -m src.weather.batch_archive --start-date 2025-11-01 --end-date 2025-12-31 --sleep-seconds 1
python -m src.weather.batch_archive --start-date 2026-01-01 --end-date 2026-01-30 --sleep-seconds 1
python -m src.weather.batch_archive --start-date 2026-01-31 --end-date 2026-02-27 --sleep-seconds 1
python -m src.weather.verify_archive --start-date 2025-11-01 --end-date 2026-02-27
```

The batch command updates the local manifest after every run and skips a run only if both its row file and raw response SHA match. It retries a failed request at most three times and spaces fresh requests by at least one second. The verifier rechecks every raw SHA, 48 consecutive selected hours, row source SHA, finite numeric variables, and the inferred issue-time gate. Observed verifier result: **119/119, 5,712 hours, no failures**.

**Provenance boundary:** availability_basis is inferred_run_plus_9h; provenance_status is unconfirmed on every row. As documented in [R03 correction](availability-correction.md), nine hours is a safety margin, not an archived publication timestamp or a guarantee of no leakage. February SCADA actuals are absent; these files are weather inputs only. Training and evaluation must enforce the C2 issue-time split on SCADA labels separately.

Source attribution: [Open-Meteo Single Runs API](https://open-meteo.com/en/docs/single-runs-api), underlying ECMWF IFS. [Open-Meteo terms](https://open-meteo.com/en/terms) specify CC BY 4.0 data and free API access for non-commercial use.
