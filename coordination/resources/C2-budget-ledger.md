# C2 resource ledger — sole writer C2

Authorization: BUDGET_AUTHORIZATION.md; shared team ceilings NVIDIA USD50 and OpenAI API USD50. No top-ups/subscriptions. Confirmed remaining account credit is UNKNOWN until panel verification.

| Time UTC+5 | Service/job | Owner | Upper estimate | Actual/source | Stop/state |
|---|---|---|---|---|---|
| 2026-09-23 14:39 | Local CPU baseline and candidate | C2 | USD0 cloud | USD0 API/GPU calls by C2 | Starting; no paid resources |
| 2026-09-23 14:47 | Local CPU completed | C2 | USD0 cloud | CPU training11.391s; baseline chosen over CatBoost variants | Stopped; no cloud compute |
| 2026-09-23 14:47 | NVIDIA Brev / OpenAI access probe | C2 | USD0 | Browser profiles visible; Brev CDP Emulation.setFocusEmulationEnabled timeout; credit UNKNOWN | No GPU/API job; C3 asks owner reconnect |

OpenAI planned model gpt-4.1-mini-2025-04-14; official docs checked 23 Sep 2026: input USD0.40/M tokens, output USD1.60/M, cached input USD0.10/M. Source: https://developers.openai.com/api/docs/models/gpt-4.1-mini . Function-calling reference: https://developers.openai.com/api/docs/guides/function-calling . Planned bounded pass max12 responses,800 output tokens/response,16000 context characters,180s outer deadline,30s/request,no SDK retries. No actual usage yet.

No paid job or API request started. Other team spending unknown; request coordination before concurrent spending. GPU setup timebox 10 minutes; local CPU path continues.
