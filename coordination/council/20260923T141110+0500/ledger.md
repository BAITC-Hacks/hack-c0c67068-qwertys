# Ledger — RUN_ID 20260923T141110+0500

Append-only, CLAUDE. Times +0500. Authoritative time = Git commit timestamp.

## Receipts

| What | Role | Commit (branch) | Commit time | On time? |
|---|---|---|---|---|
| brief | CLAUDE | 8a05503 (agent/claude-review) | 14:11 | — |
| ideas (18) | CLAUDE | c31222e | 14:12 | yes |
| ideas (10) | C4 | 7efc368 (agent/c4-ui) | 14:17 | yes |
| ideas (10) | C1 | d8ff3ee (agent/c1-data) | ~14:18 | yes (concurrent with shortlist; all mapped into S-01/S-02/S-08, no new candidate) |
| ideas | C2 | — | — | absent (not identified on laptop 1) |
| shortlist S-01..S-08 | CLAUDE | **42bb23a** | 14:18 | — |
| ballot | CLAUDE | 5e75b56 | 14:18 | yes, fixed before reading others |
| ballot | C4 | c888109 (agent/c4-ui) | 14:20:55 | yes, shortlist 42bb23a |
| ballot | C1 | 0246028 (agent/c1-data) | 14:23:07 | yes, shortlist 42bb23a (C1 replaces absent C2, per C3 ACK 2930d98) |
| extended pool (148 simulated, 1 Claude voice) | CLAUDE | 9826232 | 14:23 | B request 14:20; not voted separately |

**Independent executors voting: 3 (CLAUDE, C4, C1)** → quorum met; result is a council recommendation pending A's ratification. Composition differs from the plan (C1 instead of C2).

## Scores S = 20×(0.25K+0.25F+0.15D+0.15I+0.10V+0.05R+0.05N)

| ID | CLAUDE | C4 | C1 | median | min | max | veto |
|---|---|---|---|---|---|---|---|
| S-01 | 75 | 89 | 64 | **75** | 64 | 89 | — |
| S-02 | 74 | 84 | 64 | 74 | 64 | 84 | — |
| S-03 | 75 | 62 | 63 | 63 | 62 | 75 | — |
| S-04 | 44 | 51 | 31 | 44 | 31 | 51 | **C1 veto**: unverified extra archives, 45 min > P1 gate |
| S-05 | 72 | 76 | 75 | **75** | 72 | 76 | — |
| S-06 | 82 | 89 | 71 | **82** | 71 | 89 | — (C1 condition: cache committed only after licence/size check) |
| S-07 | 72 | 59 | 65 | 65 | 59 | 72 | — |
| S-08 | 72 | 72 | 78 | 72 | 72 | 78 | — |

C1 wrote comments into the `veto` field for S-05/S-06/S-07/S-08; read as conditions, not vetoes (their text is supportive). Only S-04 is treated as vetoed. C1 please correct by a new message if misread.

## Dissent / risk recorded

- C1 on S-01: F=2 — 150–180 min and absent C2 make the deadline fragile → stop rule 15:15 reduce to verified offline baseline.
- C4 on S-03: unsupported confidence shading would mislead → bands only with measured coverage.
- C4 on S-08: timezone test cannot prove metadata; never auto-change tz from final evaluation.
- All: `available_at = init + 6 h` is an assumption until evidenced (R03 OPEN).

## Resource use

0 external API calls for the council. 6 Claude subagent generations (no tools, no repo reads). Visible-token cap from RESOURCES_AND_LIMITS exceeded at B's explicit request for a larger pool — recorded, not hidden.
