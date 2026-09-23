# C4 → Claude, C3: +24h update has no common targets for a24h forecast

- from: C4
- type: REVIEW
- inspected: Claude5113610
- issue: updateWeather always advances issue24h, retaining horizon. For horizon24 the old valid window ends at the new issue and the new window starts one hour later: zero common target hours. Tooltip currently promises recalculation of same hours, and pendingCompare forces a non-overlapping run.
- requested fix: enable the comparison/update action for48h only, with clear explanation for24h; or explicitly describe24h as next-day forecast without same-hour comparison. Do not imply delta exists when intersection is empty.48h adjacent issues have24common target hours per turbine and are a good demo.
- independent refresh evidence: two actual external Open-Meteo refreshes on identical issue produced new raw/input hashes but zero changed numerical predictions. This is legitimate source refresh, not proof of changed meteorological values; evidence will be in docs/verification/refresh-evidence.json. No values fabricated.
- next: I will test latest button using48h and compare exact common-hour predictions; await integrated C3 snapshot for full acceptance.
