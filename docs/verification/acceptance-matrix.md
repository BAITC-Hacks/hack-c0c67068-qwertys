# Independent product acceptance — C4 / Codex2

Updated 2026-09-23 14:46 UTC+5. This is an evidence ledger, not a declaration of product readiness. PASS applies only to the stated scope. BLOCKED means a required artifact/input is absent; NOT_RUN means evidence has not yet been collected. Author claims alone do not qualify as evidence.

Environment: Windows, Python 3.12.10, Node 24.21.0, npm 11.19.0. API implementation `c572dfb`; data/weather integrated through `e48a836`; tested Claude frontend snapshot `0276529`. Latest Claude changes `cf06fe7` are not covered by the browser result below. Test fixtures are synthetic and never constitute real model acceptance.

| Requirement | Check / command | Expected | Observed | Evidence | Status |
|---|---|---|---|---|---|
| Official SCADA identity | `.venv/Scripts/python.exe scripts/verify_data.py PATH_TO_CSV_DIRECTORY` | Both manifest SHA-256 values match | Both match | `c572dfb`, local original CSV files | PASS |
| Units remain faithful | API/CSV contract inspection; transport export test | `normalized_power`; no invented MW or clipping | Value 1.2 retained in test export; unit explicit | `tests/integration/test_api.py` | PASS |
| Historical weather availability | Verify actual historical release evidence | Availability proven before each issue | Only inferred run+9h; original publication time not established | C1 `e48a836`, metadata `unconfirmed` | BLOCKED |
| SCADA timezone | Verify official timezone evidence | Offset documented by source | UTC+6 remains hypothesis | DATA_MANIFEST and C1 preparation metadata | BLOCKED |
| Input aggregation boundaries | `.venv/Scripts/python.exe -m pytest tests/test_data_weather.py -q` | Duplicates flagged, cutoff respected, coverage explicit | Two tests pass; partial sample 2/6, future samples excluded | C1 tests, independently executed 14:44 | PASS |
| Future weather and invalid outputs | `.venv/Scripts/python.exe -m pytest tests/integration -q` | Future weather, duplicate/wrong/empty/NaN/lead output fails safely | Covered negative cases fail and export is unavailable | 19 transport tests at `c572dfb` | PASS |
| Full data quality / inf / missing hours | Inspect actual hourly artifact and independent finite/coverage scan | Missingness recorded, no hidden fill | Final training artifacts absent locally | Await C1 manifest/cache transfer | BLOCKED |
| Temporal split and overlapping origins | Inspect saved split and target-hour intersections | No target overlap across train/validation/test; origins preserved | Training split/predictions not delivered | Await C2 executable/artifacts | BLOCKED |
| Train-only preprocessing | Inspect fitted transform paths/config and reproduce | Fit uses train only | Core not delivered | Await C2 | BLOCKED |
| Independent model metrics | Recompute MAE/RMSE/bias from saved predictions and labels | Match report, same-sample baseline; turbine/lead slices and counts | No model/predictions/labels artifact yet | Await C2; February has no labels | BLOCKED |
| Real 24/48h forecast | Execute official core for both turbines | 48/96 finite rows with consistent issue/lead | Synthetic transport fixture only; no real numerical acceptance | Await C2 callable READY | BLOCKED |
| Real LLM tool calling | Execute configured agent; inspect safe actual tool journal | Real request/tool/result, bounded calls and timeouts | No live agent executed by C4 | Await C2 and authorized configured runtime | BLOCKED |
| Weather / LLM failure behavior | Inject provider failures into actual core | Bounded retries and explicit failure/fallback mode | Transport handles runner exception; core behavior untested | Transport exception test only | BLOCKED |
| Recompute preserves history | Transport rerun/restart test | New run_id; old rows unchanged after restart | Pass with injected fixture | `test_forecast_export_rerun_and_restart`, 24 and 48 | PASS |
| API validation / unavailable state | Requests for invalid date, unknown run, missing core, incomplete result | 422 / 404 / 503 not_ready / 409 | Pass; no successful run manufactured without core | Integration tests + real Chrome API call | PASS |
| API–CSV numerical consistency | Parse exported CSV from same run | Same rows/numbers/unit | Tested fixture passes, including un-clipped 1.2 | Integration export test | PASS |
| Real UI–API–CSV consistency | Browser run with real core; compare all displayed/exported points | Same actual predictions | Real core absent | Await C2 + final Claude UI | BLOCKED |
| Frontend build and basic browser flow | `npm.cmd ci`; `npm.cmd run build`; headless Chrome via Playwright | Build, no JS errors, visible unavailable state, explicit synthetic demo | Build and Chrome pass; synthetic 24/48 tables and download work | Claude snapshot `0276529`; local `.local/ui-check.cjs`, screenshots | PASS |
| Polling cancellation / selection race | Inspect async UI operations; rapid selection + replay stop | Stale results cannot replace active selection; bounded polling | Source risks sent to Claude, fix pending independent verification | C4 message `20260923T144230+0500` | NOT_RUN |
| Keyboard / focus / contrast / small screen | Browser keyboard traversal and responsive check | Main flow usable and labels readable | Screenshots captured only; complete interaction audit pending | Local screenshots, no formal accessibility claim | NOT_RUN |
| Runtime dependencies | `pip check`; import numpy/pandas/catboost/openai; full pytest | Compatible imports and existing tests | Imports pass; pip check clean; 21 tests pass in 1.25s | Local environment 14:44 | PASS |
| Clean laptop-2 reproduction | New isolated environment from lock, README launch, full forecast | Build/start/real calculation from documented commands | Existing venv tested; pristine install and full forecast pending | No clean-env acceptance yet | NOT_RUN |
| Actual latency | Time first real baseline/API execution | Observed duration recorded, no guessed promise | Core absent; pytest time is not forecast latency | Await C2 | BLOCKED |
| Secret handling | Inject exception/event secrets | No keys in API status/events | Tested token patterns redacted, exception sanitized | `test_core_exception_and_event_secrets_are_not_exposed` | PASS |

Current conclusion: HTTP transport and basic frontend states work. Product acceptance is BLOCKED on the real core/artifacts and end-to-end verification. Unknown historical weather provenance and timezone remain explicit limitations even if the prototype works. No February accuracy, GPU training success, or live LLM execution is claimed.

Local QA artifacts under `.local/` are intentionally ignored; they can be regenerated on this laptop. Durable evidence is the listed source tests/commits and their recorded observed outcomes. Final acceptance will replace pending entries with exact artifact hashes, commands and measurements.
