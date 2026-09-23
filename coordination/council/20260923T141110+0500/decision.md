# Decision (council recommendation) — RUN_ID 20260923T141110+0500

Status: **RECOMMENDED, awaiting ratification by A** (`coordination/messages/<TS>-A-ratify-<id>.md`). Silence ≠ approval; P0 development continues regardless. 3 independent ballots (CLAUDE, C4, C1). Owners follow ASSIGNMENTS_NOW.md (cef6dbb): C1 data/weather, C2 model+agent, C4 env/API/QA/README, CLAUDE web/.

## P0 — S-01 "As-issued NWP → GBM → agent loop → export → one screen" (median 75)

Pipeline: hourly SCADA (UTC+6 inferred → UTC, coverage flags) → issue_time rule with `available_at = init + 6 h ≤ issue_time` → ECMWF IFS single run (source card W1) per issue → features → GBM (LightGBM/CatBoost) vs power-curve + climatology baselines on rolling-origin Nov–Jan backtest → agent loop with typed tools + JSONL journal (LLM optional, labelled deterministic mode) → recompute when a newer run is available (new run_id, old kept) → CSV export (full key turbine+issue+valid+run) → one dispatcher screen.

| Component | Owner | Gate |
|---|---|---|
| hourly SCADA + weather adapter + as-issued cache + available_at gate | C1 | 14:45 prepared inputs |
| baseline + GBM + backtest table | C2 | 14:40 baseline, 15:15 candidate |
| agent loop + CLI + recompute | C2 (C4 plumbing) | 15:45 full cycle, 16:15 Feb replay |
| FastAPI contract + env + tests + README | C4 | 14:40 contract/health, 16:15 README |
| web/ screen | CLAUDE | 14:50 first screen, 15:20 real API, 15:50 full |

**Stop rule (in-line fallback = S-02, median 74):** 15:15 no measured GBM gain or no end-to-end issue → ship per-turbine power curve on MOS-corrected NWP wind in the same pipeline/API (C4, C1, C2 stop rules agree).

Recommended acceptance details for owners, selected by CLAUDE from the 148-idea pool (non-binding, 1 Claude voice, each ≤20 min):

- TS-B11 "time machine" data access: SCADA/NWP readers take `as_of=issue_time`, return only rows ≤ as_of; Feb replay runs through it (C1/C2).
- TS-B09 guard: metrics function raises on any target ≥ 2026-02-01 (C2).
- AG-11 self-healing: weather fetch failure → retry/backoff → fall back to previous available run, status `degraded`, never `success` (C2/C4).
- NWP-04 run-to-run delta: analyze tool reports |new − previous run| on overlapping hours; large delta → recompute decision + UI note (C2; UI by CLAUDE).
- ML-11 monotone constraint on wind speed in GBM (C2, only if it does not hurt the backtest).
- LLM-09 / LLM-08: numbers only from tools; LLM text optional, with placeholders (C2).
- UX-A13 live agent stage view driven by the real event log (CLAUDE UI).
- TS-A01 / TS-A02 climatology + persistence baselines in the backtest table (C2).

## P1 (start only after P0 works and A ratifies; ≤20–25 min each, rollback = remove)

1. **S-06 Reproducibility pack + as-issued weather cache** (median 82) — owner C4 (+C1 for cache). Accept: fresh clone on laptop 2 follows README only and reproduces the export; cache committed only after licence (Open-Meteo CC BY 4.0 → attribution in README) and size check (<20 MB). Stop: 16:15 not reproducible → README/env becomes the main line.
2. **S-05 Revision compare** (median 75) — owner CLAUDE (UI), C2 provides two real runs per issue. Accept: overlay only real runs, common valid hours, run IDs shown. Stop: no real second run by 16:00 → drop.

Reserve: S-08 failure-safe rerun + timezone self-test (median 72; C4/C1) — first pick if a P1 is dropped.

## Rejected / deferred

- S-04 multi-NWP blend — vetoed by C1 (unverified archives for Feb, time) → roadmap.
- S-03 uncertainty bands (63) and S-07 alerts (65) — below the cut; may enter only via reserve after P1, bands only with measured coverage.
