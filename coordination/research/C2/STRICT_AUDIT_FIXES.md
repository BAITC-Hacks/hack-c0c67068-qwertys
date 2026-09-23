# C2 — fixes for strict audit F5/F6/F7/F8

Base: coord798bfb9. Scope: src/ml, src/agent, own regression tests; coordinator explicitly authorized only the safe_summary import replacement in src/api/main.py.

## Changes

- Both file-backed and direct `predict_from_inputs` calls use one `available_horizon` gate. It checks complete horizon/source/schema through the existing weather validator and rejects publication before run+9h or after the issue. The lag constant is shared with the weather adapter. This enforces the declared assumption; it does not prove historical publication.
- `input_version` includes the parsed model manifest (actual curve values and feature masks), request, selected weather and SHA256 of actual CatBoost bytes. CatBoost inference loads the same byte buffer being hashed. Optional declared model checksum remains enforced. Existing model_version stays unchanged; previously pinned input_version values must be refreshed because the identity formula is stronger.
- `src.agent.safety.safe_summary` redacts nested JSON secret keys structurally, including escaped keys/values, and covers mixed diagnostic/plain credential text. Core events are sanitized before persistence and truncation. API imports the same sanitizer; no other API behavior was edited.
- Free LLM final text is never copied to events. `agent.summary` is composed by code from the completed five-tool workflow and actual row count/horizon/model, with explicit provenance and February-label limitations. Incomplete workflows cannot produce this summary. It reports staged export accurately; normal successful finalization still follows.

## Verification

`python -m pytest tests --ignore=tests/test_deep_compare.py --ignore=tests/test_quality_cycle.py -q` → **85 passed, 4 subtests passed (3.21s)**. Optional training tests intentionally not run under the no-training instruction. The new regression file contains16cases, including an API JSON-secret event persisted in SQLite and read again after restart. Fake LLM/CatBoost fixtures make no network calls and fit no models.

Original `strict-audit-20260923/system_audit.py` was copied into an ignored artifact directory; only ROOT changed to this worktree. **20/23 checks PASS**. Every assigned defect now passes: `direct_callable_enforces_nine_hour_gate`, `input_version_covers_actual_curve_parameters`, JSON password/token redaction and unsupported LLM claims. The three remaining failures are expected outside this patch: upstream temperature/direction units, missing upstream units (C1), and advertised arbitrary-hour coverage (UI/coordinator). The original audit files were not modified.

Offline numerical compatibility: all96 V1 predictions exactly match the previously verified clean-export result; input_version changes as intended. Existing extended-V2 CatBoost checkpoints load via blob and return96 finite forecast rows without retraining. These are inference checks, not a new accuracy evaluation or production model promotion.

No training, new external requests, paid API or GPU use. No model weights/metrics changed. `git diff --check` PASS. Historical availability, SCADA timezone and absence of February labels remain unresolved data limitations.

Evidence: `strict-audit-fixes.json`. Raw local audit artifacts: `artifacts/strict-audit-fixes/` (ignored; contains local forecasts, not published).
