# Council brief — RUN_ID 20260923T141110+0500

- from: CLAUDE (laptop 2, branch `agent/claude-review`)
- start: 2026-09-23 14:11 Asia/Qyzylorda (+0500); **hard end 14:31** (min(20 min, 14:35))
- base commit read: `d52a3a6` (coord/hackalem-start)
- quotas: API/NVIDIA budget UNSET → council makes **0 external API calls**; uses existing sessions only

## Timeline (absolute)

| Until | Step | Who |
|---|---|---|
| 14:18 | Independent ideas → `ideas/<ROLE>.md` in own branch, push, message | CLAUDE, C2, C4 (C1/C3 optional, ≤2 short facts) |
| 14:21 | Shortlist 5–8 → `shortlist.md` (SHA announced by message) | CLAUDE |
| 14:25 | Ballots → `votes/<ROLE>.json`, referencing shortlist SHA; do not read others' votes first | CLAUDE, C2, C4 |
| 14:28 | Ledger, medians, veto | CLAUDE |
| 14:31 | `decision.md`: 1 P0 line + ≤2 P1; A ratifies by `...-A-ratify-...md` | CLAUDE → A |

Late ideas/ballots after the cut are recorded as late, not counted. Fewer than 3 independent ballots → result is a **preliminary recommendation**.

## Ideas file format (≤1500 tokens, 9–16 ideas)

`- ID <ROLE>-NN | title | what exactly | expected result | acceptance check | minutes (impl + integration/check) | owner | risk / unknown`

## Ballot

As in `coordination/CLAUDE_COUNCIL.md` (K,F,D,I,V,R,N 0–5; S = 20×(0.25K+0.25F+0.15D+0.15I+0.10V+0.05R+0.05N)).

## Known facts relevant to voting (status per coordination/RESEARCH.md)

- VERIFIED: no February actuals; train CSV ends 2026-01-31 23:50; 10-min input, hourly output; 2 turbines share one Open-Meteo grid cell (C1).
- REPORTED (C1 + dev1, reproduced by CLAUDE 14:08 today): Open-Meteo Single-Runs `models=ecmwf_ifs&run=2026-01-31T00:00&forecast_hours=72` → HTTP 200, hourly `wind_speed_100m` etc. Provenance (operational vs hindcast) and **available_at** still OPEN (R03). Rule proposal: run init + 6 h latency ≤ issue_time.
- REPORTED (dev1): Previous-Runs API (`*_previous_day1/2`) for ECMWF/GFS/ICON exists from ~2024-03 — candidate for leakage-free-ish **training** set; R04 OPEN.
- REPORTED (dev1): SCADA fixed UTC+6 (R02, sensitivity ±1 h required); ACF(24 h)≈0.1 → NWP is main signal.
- OPEN: normalization/rated power (R07) → output stays in normalized units.

## Participants

| Role | Executor | Delivery |
|---|---|---|
| CLAUDE | this session, laptop 2 | direct |
| C4 | Codex2 in VS Code, laptop 2 | via participant B (relay prompt below) |
| C2 | Codex, laptop 1 | via participant A |
| C1/C3 | Codex, laptop 1 | optional ≤2 short fact answers |

### Relay prompt for C2 / C4 (copy as is)

> Council RUN_ID `20260923T141110+0500`. Read `coordination/CLAUDE_COUNCIL.md` + `coordination/council/20260923T141110+0500/brief.md` on `origin/agent/claude-review`. ≤3 min total. By **14:18**: write 9–16 ideas (your expertise, doable today) to `coordination/council/20260923T141110+0500/ideas/<ROLE>.md` in YOUR branch, commit, push, add message `coordination/messages/<TS>-<ROLE>-IDEAS-...md`. Do not read other ideas first. By **14:25**: after shortlist SHA is announced, write `votes/<ROLE>.json` per the ballot schema. Continue your main work; do not start P1 before A ratifies.
