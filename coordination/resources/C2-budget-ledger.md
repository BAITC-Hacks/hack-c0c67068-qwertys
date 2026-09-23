# C2 resource ledger — sole writer C2

## Current state — 2026-09-23 15:44 UTC+5

- One user-deployed Brev environment47y85unm3, created15:21:27, still Running. AWS T4 16GB; actual Tesla T4 15360MiB, driver595.91.07. Rate panel verified15:43: $0.65/hour ($0.63 compute+$0.02 storage previously itemized).
- At15:43 elapsed21min33sec since creation: approximately$0.2335 at displayed hourly rate; billing rounding/settlement may differ. Panel still displays$50.00 credit, therefore this is NOT a settled remaining balance. Conservative estimated remaining from original$50: $49.7665 before other provider charges.
- Latest direct user instruction15:38 explicitly requests another bounded quality cycle. C3 ACK15:41 supersedes previous15:51:27 stop: results16:30, one existingGPU stops no later than16:40. Maximum creation-to-new-stop78min33sec ≈$0.8510 at displayed rate; no added machines, top-ups or increased$50 ceiling.
- CUDA project DL completed115.418s; CPU equivalent614.75s. Actual weights/reports archived on GPU; local export pending. Initial failed setup repaired via official uv/Python3.12, torch2.14cu126, numpy2.5.3, catboost1.2.10. No account keys or git credentials uploaded.
- Storage persists after compute Stop at approximately$0.02/hour ($0.48/day). Do not claim zero ongoing charge after Stop. Export and deletion decision remain separate.
- OpenAI cumulative actual-token estimate unchanged$0.0060296; no new API calls or subscriptions in this quality cycle so far.

Historical entries below remain as recorded; this current-state section supersedes their old GPU pending/stop status.

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

## Confirmed update 2026-09-23 15:24 UTC+5

- Two additional **browser-originated live UI/API** runs completed: API25c182d9622e445da659dc8282746877 -> agent79f7c1cda642443b9d1a0b2f05c17f25, 96 rows; API65d1b212eee445f8b61405a68f5c1275 -> agentac469e4b49a44cd4a2e8013ec234ba24, 48 rows. Six real responses and five actual tools each. Combined estimated cost $0.0030816. Exact token/response evidence in research/C2/live-ui-api-evidence.json.
- Cumulative API estimate **$0.0060296**, derived from actual usage, not a reread of settled billing. No new credit purchase or subscription.
- Local CPU DL research uses no cloud charges. Optional torch2.14.0+cpu installed from official PyTorch index (124MB wheel).
- User requested a pre-Deploy check and said they would press Deploy themselves. Prepared configuration reverified: one AWS T4,128GiB,$0.65/hour,$50 balance shown. Setup saved at pinned b05bc81; Python environment + CatBoost1.2.10 + numpy2.2.6 + PyTorch2.14.0 CUDA12.6, nvidia-smi and real GPU forward/backward smoke. Actual driver/CUDA readiness unverified until boot.
- New private DL input544113bytes SHA256 b4d01f11d33d485c1a36940b849ba345300698fa306ac98ffcb25749d5458dc0. No upload yet. No GPU deployment/spend claimed; maximum one machine and planned stop within30min remain.
