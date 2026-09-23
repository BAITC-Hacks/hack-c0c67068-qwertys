# Shortlist — RUN_ID 20260923T141110+0500

Cut for ideas: 14:18. Received: **CLAUDE** (18, `c31222e`), **C4** (10, `origin/agent/c4-ui` `7efc368`). C2: no ideas file on remote at 14:18 → absent. C1: invited by C3 ACK (`2930d98`) as replacement voter; ideas not received by cut → C1 may still vote on this shortlist.
Total raw ideas: 28 (below 30–50 target — recorded as incomplete generation, not padded).

Each candidate below is voted as a whole. P0 candidates are complete lines; P1 are independent add-ons that start only after P0 works and A ratifies.

| ID | Type | Candidate | Merged ideas (authors) | Acceptance check | Proposed owner | Est. min (impl+check) |
|---|---|---|---|---|---|---|
| S-01 | P0 line | **As-issued NWP → GBM → agent loop → export → one screen.** Hourly SCADA (fixed UTC+6 inferred → UTC, coverage flags, downtime flag); issue D 00:00 local uses latest ECMWF IFS single run with init+6 h ≤ issue_time (conservative available_at); training features from the same kind of archived forecasts (single runs or previous-runs day1/day2), never ERA5 at inference; LightGBM/CatBoost vs power-curve & climatology baselines on rolling-origin Nov–Jan backtest; deterministic agent loop with typed tools (check_new_run → fetch → validate → features → predict → analyze → decide → report) + JSONL journal, optional OpenAI tool-calling, labelled no-LLM mode; recompute when a newer run becomes available (new run_id, old kept); CSV with full key; one dispatcher screen with provenance strip, honest mode banner, event timeline, coverage warnings, separate history-only metrics panel | CLAUDE-01,02,03,05,06,07,08,09,15; C4-01,02,03,04,05,07,08 | 29 issues × 48 h × 2 turbines exported; Q03 `available_at ≤ issue < valid` holds on all rows; backtest table vs baselines; journal shows real tool calls; rerun creates new run_id | C1 data/weather, C2 model (C3 if C2 absent), C3 agent/API, C4 UI | 150–180 total parallel |
| S-02 | P0 alt | **Physics-first line**: identical pipeline, but model = per-turbine empirical power curve applied to MOS-bias-corrected NWP wind (no GBM) | CLAUDE-04 | same as S-01 minus GBM; backtest vs climatology | C2/C3 | 120–140 |
| S-03 | P1 | Uncertainty band P10/P90 (quantile GBM or conformal by lead bucket), empirical coverage reported on backtest; hidden if not calibrated | CLAUDE-11 (C4 constraint: no intervals without evidence) | coverage of P10–P90 on backtest printed; UI shows band only with that number | C2 | 25 |
| S-04 | P1 | Multi-NWP blend (GFS/ICON/AIFS via previous-runs) with per-source model + average | CLAUDE-12 | backtest gain vs S-01 on same hours; Feb availability proven per source | C1/C2 | 45 |
| S-05 | P1 | Revision compare: overlay two real runs of the same issue on common valid times + delta table | CLAUDE-08 (visual part), C4-09 | IDs and timestamps match; only real runs | C4 | 25 |
| S-06 | P1 | Offline weather cache committed + clean-clone reproducibility pack (one command, pinned deps, `--offline` replay reproduces committed export) | CLAUDE-10,16 | fresh clone on laptop 2 by B, log in docs/verification | C1 + CLAUDE/B | 20 |
| S-07 | P1 | Operator alerts + daily RU summary (cut-out risk, ramps, icing if RH available, low-confidence), template or LLM text, numbers from code only | CLAUDE-13 | flags present in export + UI; no LLM-invented numbers | C3 | 15 |
| S-08 | P1 | Failure-safe rerun: failed rerun keeps previous result with label; timezone self-test tool (SCADA↔NWP lag −3…+3 h) warns at startup | C4-06, CLAUDE-17 | simulate failure after success → previous plan intact; lag printed | C3/C1 | 20 |

Folded into S-01 (not voted separately): CLAUDE-14 (screen), C4-10 (keyboard/narrow screen = UI polish inside C4 scope).
Roadmap only (not voted): CLAUDE-18 (TSFM Chronos-2/TiRex, MW aggregation after R07, live mode).

Veto screen applied (CLAUDE_COUNCIL §Отсечения): none of S-01…S-08 uses Feb actuals or reanalysis at inference. **Open dependency for every candidate: R03 available_at of ECMWF single runs** — carried as risk, not vetoed (C1 evidence `1bc29c1`: 49r1 operational since 2024-11-12; run = init time, +4–6 h latency).

Ballot: `votes/<ROLE>.json` in your own branch, schema from CLAUDE_COUNCIL.md, `shortlist_commit` = SHA announced in the message. **Deadline 14:25.** Do not read other ballots first.
