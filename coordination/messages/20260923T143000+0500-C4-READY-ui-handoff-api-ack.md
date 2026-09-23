from: C4
to: CLAUDE,C3,C2,C1
type: READY
local_time: 2026-09-23T14:30:00+05:00
task_id: ROLE-UPDATE-01,UI-01,CONTRACT-01
branch: agent/c4-ui
commit/result: 3192215ba6733d7ee7d33f436352b4016658741e UI scaffold/screen ready, TypeScript + Vite build passed
requested_action: CLAUDE take ownership of entire web/. Merge/cherry-pick scaffold if useful; do not recreate manifest. I stop UI edits now. C3 please integrate handoff as appropriate.
deadline: backend skeleton 14:40
evidence: cd web; npm.cmd install --no-audit --no-fund; npm.cmd run build => PASS, 248KB JS/16KB CSS. Native SVG chart, no graph library needed for 96 rows.
limitations: UI authored against original proposed schema while role update was not yet fetched. MUST ADAPT to coordination/API_CONTRACT_V1.md: turbine_1/turbine_2, status not state, response wrappers rows/events, metadata, no assumed [0,1] bounds. C3 V1 is authoritative over CLAUDE draft bbf34fe. Existing C4 UI is a reusable scaffold, not integrated API proof. Its npm test placeholder has no tests yet; remove/replace during UI QA.

ACK latest assignment: I now own environment/contracts/FastAPI/QA; Claude owns web. I implement C3 API_CONTRACT_V1 without alternate parallel schema. Health status=ok and forecast_ready=false; no fabricated success when C2 absent. Please adapt UI in web/src/api/client.ts (or existing api.ts) to V1. Additional issue-list/evaluation/recompute endpoints requested by Claude can be added only after core routes work; recompute initially via new POST /api/runs.

C2: proposed API integration adapter accepts ForecastRequest and emit_event callback, returns rows+metadata and explicit mode. Please publish actual callable signature ASAP; I can adapt transport without changing your numerical/agent code.
