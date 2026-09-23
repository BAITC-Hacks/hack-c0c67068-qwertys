# C2 resource ledger — sole writer C2

Authorization: BUDGET_AUTHORIZATION.md; shared team ceilings NVIDIA USD50 and OpenAI API USD50. No top-ups/subscriptions. Confirmed remaining account credit is UNKNOWN until panel verification.

| Time UTC+5 | Service/job | Owner | Upper estimate | Actual/source | Stop/state |
|---|---|---|---|---|---|
| 2026-09-23 14:39 | Local CPU baseline and candidate | C2 | USD0 cloud | USD0 API/GPU calls by C2 | Starting; no paid resources |
| 2026-09-23 14:47 | Local CPU completed | C2 | USD0 cloud | CPU training11.391s; baseline chosen over CatBoost variants | Stopped; no cloud compute |
| 2026-09-23 14:47 | NVIDIA Brev / OpenAI access probe | C2 | USD0 | Browser profiles visible; Brev CDP Emulation.setFocusEmulationEnabled timeout; credit UNKNOWN | No GPU/API job; C3 asks owner reconnect |

OpenAI planned model gpt-4.1-mini-2025-04-14; official docs checked 23 Sep 2026: input USD0.40/M tokens, output USD1.60/M, cached input USD0.10/M. Source: https://developers.openai.com/api/docs/models/gpt-4.1-mini . Function-calling reference: https://developers.openai.com/api/docs/guides/function-calling . Planned bounded pass max12 responses,800 output tokens/response,16000 context characters,180s outer deadline,30s/request,no SDK retries. No actual usage yet.

No paid job or API request started. Other team spending unknown; request coordination before concurrent spending. GPU setup timebox 10 minutes; local CPU path continues.

## Confirmed update 2026-09-23 14:57 UTC+5 (supersedes no-call status above)

- OpenAI Ash panel: Personal Organization, credit$50.00, auto-reloadOFF, tier2, current monthly spend$0.00 shown before smoke. No billing settings changed. Successful real model access confirmed by calls below.
- Live48h run a4a9a157ff374d0ba137f9bda719efe1:6responses,2798input/211output,$0.0014568 estimated from actual token usage; completed96rows.
- Live24h+fresh-weather run a072d05677b648abae9b85167d21adab:6responses,2796input/233output,$0.0014912 estimated;11.297s;completed48rows.
- Cumulative API estimate$0.002948. Dashboard balance not re-read after these calls, so confirmed remaining credits not claimed to the cent. Local usage ledger `artifacts/openai-usage.json`; per-run reservation$0.20, cumulative local default cap$1, no SDK retries; unknown model tariff rejected.
- NVIDIA Magician access restored using new controlled tab; Brev organizationQwertyS Billing currentbalance$50.00 and totalcost$0.00. No environment exists yet. Prepared1×T4/16GB VRAM,AWSg4dn.xlarge,16GiBRAM4CPU,128GiBdisk,$0.63compute+$0.02storage=$0.65/hr. Planned≤30min≈$0.325plus any residualstorage. Stop and disk-billing check required after experiment.
- Deploy not pressed: one pending user confirmation for explicit AWS personal/deployment-data consent, separate from already-authorized spending. Dataset115951bytes SHA94d90c8150e4499c2b1e388e31658366918c9ca973a2df551d05abf60966704a; pinned code d7d8a68; no upload yet. CPU hardware-reproduction1.594s;GPU not run.
