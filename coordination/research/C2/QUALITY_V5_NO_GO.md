# V5 result — NO-GO before training

Research branch `agent/c2-quality-v5`; frozen protocol `4e4cd06`. Production V1/backend746a0a8 and demo8010 unchanged. No candidate code, model fitting, new weights, forecasts or quality metrics were produced.

The one existing Brev environment47y85unm3 restarted: Starting17:16:12, Running17:16:23 UTC+5. Jupyter opened, but the real CUDA tensor probe had not returned by the frozen17:18:59 readiness deadline. The reason for the missing response was not established; this is an unconfirmed readiness probe, not a proven GPU hardware failure. Per the precommitted stop rule, no training was started and there was no retry with another machine.

Stop requested17:19:42; provider History confirms **Stopped17:24:32**, within the12-minute hard deadline17:27:59. Shutdown took4m50s. An earlier stale page continued to show Stopping; a fresh reload verified the final History. C3 independently verified Stopped at17:32.

Restart-to-Stopped8m20s at the previously displayed full rate$0.65/hour gives a conservative **$0.0903 estimate** for this cycle, not settled billing. The refreshed account balance showed$49.55; its change includes settlement of earlier activity and is not attributable solely to V5. Storage continues at$0.02/hour ($0.48/day); irreversible deletion remains pending separate user confirmation. No top-up, additional instance, API call or dataset upload.

The three proposed wind-regime calibration candidates remain an unexecuted preregistered protocol. There is no measured quality improvement to report, no promotion, and no new deployable backend/model commit. V1 remains the accepted production model. No further GPU restart under this cycle.
