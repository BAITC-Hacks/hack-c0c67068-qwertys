# C2 READY — final core, quality evidence and GPU stop

To: C3 / C4. Published artifact commit: `4c07544`, branch `agent/c2-ml`; includes common integration `bd8293a` and same-CUDA evidence `3750b69`.

- V1 remains production. V4 failed both frozen quality gates; C5 independently confirms this in `053c54e`. No new fits or threshold changes.
- Actual T4 GPU training: 60 saved outer neural checkpoints over V3/V4 plus 12 GPU CatBoost models. Both result archives and prediction evidence downloaded and verified. Research evidence is separate from production artifacts.
- Final suite: 77 tests and 4 subtests PASS. Final real browser path: 96 rows, six LLM responses, five actual tools, exact API/CSV match, retained earlier runs, empty browser error/warn log. UI assets index-Bu6gZIe7.js / index-O7nCWpHI.css. Evidence `coordination/research/C2/final-live-ui-evidence.json`.
- Strict-weather replay: 29 issues / 2784 journal rows / 1344 February rows; final CSV SHA256 `da6730f17ab48ad19bcb169725bc5eeab872b95fe9713ecf42a3bdc8c4801996`.
- Brev provider History confirms Stopped at 16:05:12 UTC+5. Storage still $0.02/hour; irreversible deletion awaits user answer. Updated sole-writer resource ledger and status replace stale pending-export/running claims. No settled-cost claim; displayed credit49.91 may lag.
- Pending integration: C3 merge `4c07544` and C5 `053c54e`, ACK the core handoff; C4 retains MODEL_DIR pointing to V1. Integration deadline17:00 unchanged. Local verified demo http://127.0.0.1:8010/ remains available.

Known boundaries: weather historical availability and SCADA UTC+6 inferred, no February observations, normalized power/capacity unconfirmed. V4 inner calibration artifacts not exported; alpha source/masks/application inspected, optimum not independently refitted. No external big-tech benchmark claim.
