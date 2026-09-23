# C2 execution and limits

Use the shared C4 Python manifest/lock. Observed local runtime Python3.12.14, numpy2.5.3, pandas3.0.6, catboost1.2.10, openai3.19.0, python-dotenv1.2.3. Production chose a learned NWP wind-bin curve after two pretest folds; CatBoost did not win. Model artifact `model-manifest-v1.json` is a small self-contained JSON and can be copied to ignored `models/production/manifest.json` for inference. No raw labels in Git.

## Train and independent evaluation

```
python -m src.ml.train --scada-dir <C1_hourly_dir> --weather-dir <C1_weather_runs> --output-dir models/production --report artifacts/evaluation/evaluation.json
python -m unittest discover -s tests -v
```

SCADA input files: scada-t1-hourly.jsonl and scada-t2-hourly.jsonl, produced by C1 adapter from official locally supplied CSV. Weather input: YYYY-MM-DD.jsonl, C1 batch archive. Training joins complete hourly labels only. Evaluation target intervals are disjoint; evaluation issues must also be at/after fit cutoff. Overlapping forecasts count as distinct issue/target pairs. Pretest folds Dec1–14 and Dec15–31; fixed3-trial CatBoost grid plus wind-only baseline; choose on unweighted mean fold RMSE. Refit before frozen January evaluation. Bias is mean(prediction-actual), no MW/capacity denominator. `evaluation-v1.json` records all metrics/config/versions/input hashes. Private `artifacts/evaluation/turbine_*-test-predictions.csv` allows independent exact metric recomputation. January test is now opened; any further experiment must disclose that fact. GPU comparison is hardware reproduction, not a new untouched test or model reselection.

## Numeric and agent

```
python -m src.cli --issue-time 2026-01-31T12:00Z --horizon-hours 48 --model-dir models/production --weather-dir <C1_weather_runs> --agent-mode deterministic
python -m src.cli --issue-time 2026-02-01T12:00Z --horizon-hours 24 --model-dir models/production --weather-dir <cache_dir> --agent-mode live
```

`run_forecast(request,emit)` matches C4 ForecastPayload; `readiness()` checks configured artifacts. `.env` loads through python-dotenv with override=False for both CLI/core; C4 also loads it at API startup. Keep OPENAI_API_KEY only locally; never paste in logs or Git. Set `AGENT_MODE=live` for required real LLM or `deterministic` for explicit no-LLM; auto uses live when key exists. API runner `FORECAST_RUNNER=src.agent.runner:run_forecast`.

`MODEL_DIR=models/production`, `WEATHER_RUNS_DIR=data/cache/weather_runs`, `FORECAST_OUTPUT_DIR=artifacts/runs`. `WEATHER_FETCH_POLICY=never` defaults to offline cache; `missing` invokes C1 real Open-Meteo probe if absent; `refresh` fetches a new response and validates before atomically replacing that cycle. Use an owned cache directory for refresh, not another agent's workspace. Locations use the C1-verified shared grid. Network/weather failure propagates; no fake forecasts. Current single-runs cache is intended for daily12Z issues; other times fail if the cached horizon does not cover them.

OpenAI model defaults to gpt-4.1-mini-2025-04-14. Unknown tariff fails before network. Max12 responses,800 output tokens each,16000 history characters,30s per call,180s loop,no SDK retries. Local exclusive budget lock reserves$0.20/run; default cumulative session cap$1 (`OPENAI_SESSION_BUDGET_USD`, never above authorized$50). Uncertain failed requests retain conservative reservation. Separate team resource ledger remains authoritative for nonlocal spending. Raw provider exceptions never printed by CLI/API. Usage and events persist on failure; *.partial exports cannot appear as successful final CSV after LLM failure.

## Sequential February replay

```
python -m src.cli.replay --model-dir models/production --weather-dir <C1_weather_runs>
```

29 issues Jan31–Feb28 daily12Z,96rows/issue=2784 full rows. Keep all overlaps/origins. Target February calendar assumes fixedUTC+6: Jan31 18Z inclusive throughFeb28 18Z exclusive. Selected1344rows (672/turbine) use newest stored issue with positive lead1..48. This selection/calendar is PROPOSED, not organizer-confirmed. Official case says next24–48h and daily sequential issues; it does not specify origin hour or merged-submission selection. `--min-lead-hours24` is a distinct strict day-ahead selector and requires a model with an earlier cutoff for Jan30 warm-start; current production correctly rejects that earlier issue. Full journal stays available for alternate selectors.

Historical weather publication remains unconfirmed; available_at=run+9h is inferred. UTC+6 is inferred. No February labels or measured February metrics. Numeric output is normalized power, not energy; values are not arbitrarily clipped.

## Verified live evidence

`live-smoke-v1.json`: real48h2-turbine96row pass,6OpenAI responses,5tools,2798input+211output tokens,$0.0014568 estimated.
`live-network-smoke-v2.json`: real24h2-turbine48row pass with initially empty owned weather cache,6OpenAI responses,5tools,2796input+233output,$0.0014912 estimated,11.297s. IDs/timestamps and actual tool events recorded. These are not mocked tests. Total first two passes$0.002948estimated; billing may lag. Failure unit tests are explicitly synthetic.
