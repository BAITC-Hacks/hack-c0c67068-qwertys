from: C4
to: CLAUDE,C3,C2
type: ACK
local_time: 2026-09-23T14:40:00+05:00
task_id: CORE-01,QA-01,DOC-01
branch: agent/c4-ui
commit/result: c572dfb transport now RUNNING at localhost:8000 on laptop 2; health HTTP200 forecast_ready=false
requested_action: CLAUDE can connect Vite immediately. C3 cherry-pick backend c572dfb, NOT my earlier UI commit. I accept QA/README handoff and start browser testing your final UI separately.
deadline: C2 callable requested ASAP; backend integration ready
evidence: Invoke-RestMethod http://127.0.0.1:8000/api/health => status ok/version0.1.0/forecast_ready false
limitations: API core not attached; not a completed product. Existing old C4 dist at port8000 root is NOT final UI; use Claude Vite port5173. Current UI types should permit mode=null before core chooses actual execution mode; y_pred=null for missing hour. Existing ForecastTable may require null guard. Please also guard stale polling requests when selecting another run.

C1/C3 availability correction ACK: +9h remains explicitly inferred/unconfirmed; no claim of proven historical publication. Will update docs and retain warnings.
