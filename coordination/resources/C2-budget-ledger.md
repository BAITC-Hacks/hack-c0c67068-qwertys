# C2 resource ledger — sole writer C2

## Current state — 2026-09-23 16:05 UTC+5

- One user-deployed Brev environment47y85unm3, created15:21:27, provider History confirms **Stopped at16:05:12**, observed16:05. Successful Stop transition entered16:00:25 and took4m48s. The earlier attempt returned to Running, so it was not treated as success.
- Actual Tesla T4 15360MiB, driver595.91.07. Running rate $0.65/hour ($0.63 compute+$0.02 disk). Creation-to-Stopped43min45s gives a conservative all-period estimate **$0.4740**, before provider rounding/other charges; this is not settled billing. Panel displays **$49.91** credit, potentially delayed. The authorized shared ceiling remains $50; no additional machines, top-ups or subscriptions.
- Panel now displays **$0.02/hour** disk storage ($0.48/day). Stop does not remove this charge. All artifacts have been exported and verified; specific confirmation for irreversible environment deletion is pending. No deletion performed without that answer.
- V3 CUDA research completed115.418s, V4 completed107.970s. Total60 outer DL checkpoints plus12 GPU CatBoost models exported. CPU V3 took614.75s; differing early stopping means that runtime ratio is not an equal-work benchmark. Input/ZIP/weight/CSV hashes verified locally. Same-device V3 CUDA restore measured max error0.0 over24weights. No account keys or Git credentials uploaded.
- Final browser-originated live run31ecc157653948728b3e599a61741ab0: six responses,2846input/181output tokens, estimated **$0.001428**. Cumulative C2 OpenAI actual-token estimate **$0.0074576** including preceding four live runs; billing panel not reread after calls. No new model-fitting API charges.
- User quality-cycle request15:38 and C3 ACK15:41 superseded previous15:51 stop; the revised16:40 hard stop was met. Both quality gates failed, V1 retained, search stopped. No further paid computation planned.

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
