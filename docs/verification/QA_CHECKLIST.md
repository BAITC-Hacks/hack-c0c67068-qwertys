# QA checklist (CLAUDE, QA-01)

Status: PREPARED 14:15 — nothing executed yet (no implementation code exists at d52a3a6).
Each check → exact command, observed result, commit, owner of defect. Blocking = must be fixed or declared before 17:00.

| ID | Area | Check | How | Blocking |
|---|---|---|---|---|
| Q01 | Case scope | Both turbines, hourly rows, 24 h and 48 h horizons, issues 2026-01-31 … 2026-02-28 (29 issues) | count rows per (turbine, issue); expect 48 valid hours per issue | yes |
| Q02 | Feb coverage | every Feb target hour 2026-02-01 00:00 … 02-28 23:00 (672 h × 2 turbines = 1344 pairs) covered by ≥1 issue; stated rule which issue is "the" forecast for a target hour | pivot export | yes |
| Q03 | No future weather | for every row: `weather_available_at ≤ issue_time < valid_time`; run_time alone is not accepted as available_at | assert over export | yes |
| Q04 | No Feb actuals | no code path reads SCADA after issue_time; model features for Feb contain no power/wind lags from Feb | grep features + run with SCADA truncated at issue_time → identical output | yes |
| Q05 | Timezone | SCADA tz stated (hypothesis UTC+6), weather in UTC, export tz explicit (ISO with offset) | inspect export header/values | yes |
| Q06 | Units | output = normalized active power [0,1], never MW/MWh; clipped to [0,1] | min/max of y_pred | yes |
| Q07 | Aggregation | 10-min → hourly rule documented (mean, coverage threshold, hour labelling start vs end) | code + README | yes |
| Q08 | Honest metrics | MAE/RMSE only on a pre-Feb holdout with as-issued NWP; baseline(s) on identical hours; no Feb metrics anywhere (UI, README, logs) | grep "MAE" in outputs/README/UI | yes |
| Q09 | Agent tools real | journal shows real tool calls with inputs summary, outputs, state transitions, retries; not a pre-written log | run live, compare timestamps/run_id | yes |
| Q10 | Re-run on update | new weather run → new run_id, old result kept, diff visible | trigger update, list runs | yes |
| Q11 | Failure honesty | weather API down / bad run / null values → status=error or fallback flag, never "success" with zeros | block network or bad date, observe status | yes |
| Q12 | LLM optional | without `OPENAI_API_KEY` the full pipeline runs (deterministic mode, labelled); with key, same numbers | run twice, diff forecasts | yes |
| Q13 | Secrets | no keys in repo/logs; `.env.example` only placeholders | `git grep -I -E "sk-|api_key\s*=\s*['\"][A-Za-z0-9]"` | yes |
| Q14 | Data policy | raw CSVs not committed; README says where to put them + SHA-256 from DATA_MANIFEST | `git ls-files | grep -i csv` | yes |
| Q15 | Reproducibility | fresh clone + README steps only → replay + export on laptop 2 (Windows, Python 3.12) | B + CLAUDE, log in docs/verification/clean_run.md | yes |
| Q16 | Offline mode | if network is unavailable at review, cached as-issued weather reproduces committed forecast | run offline | no (strongly desired) |
| Q17 | Export | CSV opens, columns documented, one row per (turbine, issue, valid_time) | open file | yes |
| Q18 | UI truthfulness | UI marks saved vs live run, units, weather run/provenance, no invented numbers | click-through | yes |
| Q19 | Overlap rule | 48 h horizons overlap next issue's first 24 h; duplicates by (turbine, valid_time) are NOT deduplicated in journal | check keys | yes |
| Q20 | Determinism | repeated replay with same inputs → identical predictions (seeded) | run twice, hash export | no |
