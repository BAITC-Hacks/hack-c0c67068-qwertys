# CLAUDE status

role: CLAUDE — design + frontend `web/` (per ASSIGNMENTS_NOW / C3 DECISION ROLE-UPDATE-01); council closed
owner: participant B (laptop 2, git identity nurkhanaimukatov — also author of `dev1`)
host: laptop-2
branch: agent/claude-review (worktree `hackalem-claude`)
state: UI READY on C4 transport; waiting for C2 FORECAST_RUNNER to show real forecasts
write scope: web/, coordination/council/, coordination/status/CLAUDE.md, own messages, coordination/research/CLAUDE/

Done:
- COUNCIL-01 closed 14:25: decision 454a9b7 (P0 S-01, P1 S-06 + S-05), 3 independent ballots; awaiting A ratification.
- UI-01: one dispatcher screen + February replay panel, wired to C4 API (c572dfb). Checked against real API (not_ready honest) and dev-only mock (lifecycle, recompute overlay, replay 29 issues, failure cell).

Run UI: `cd web && npm ci && npm run dev` → http://localhost:5173 (proxy /api → 127.0.0.1:8000, override VITE_API_TARGET).

Open for C3/C4: serve prebuilt `web/dist` from FastAPI so the jury needs no Node — decide whether to commit `web/dist` at freeze (≈0.6 MB) or build in README.

Next: when C2 runner lands — real run, recompute, replay; screenshots for demo; fix defects.
