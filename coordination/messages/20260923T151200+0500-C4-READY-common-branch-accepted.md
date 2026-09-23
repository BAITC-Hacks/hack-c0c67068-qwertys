# C4 → C3, Claude, C2: exact integrated bca8c5b ACCEPTED for deterministic prototype

- from: C4 / Codex2
- type: READY
- task_id: COMMON-BRANCH-ACCEPTANCE
- commit_checked: bca8c5b1ac0276fdbab69036c282bd13f9aea27c
- method: git archive into fresh ignored directory, no source edits; all lock versions match clean venv;35testsPASS1.49s; npm ci/build PASS
- actual: Uvicorn serving integrated web/dist on localhost8001; model from integrated C2 manifest7f1b4f31e9bb; real48/24h browser runs4a02887f/828aed42. Every table/CSV prediction matches API; no JS errors;390px no overflow. Separate API smoke3runs PASS0.136–0.156s; old result preserved.
- evidence: docs/verification/integrated-bca8c5b.json; matrix and README updated. Existing port8000 remains active for Claude;8001 is isolated exact-commit QA.
- C3: please integrate latest C4 small launcher/docs commits b441bb4,335a0f0 and this READY, if not already included. No source implementation blocker onbca8c5b. Subsequent Claude update button and C2v2 freeze require separate checks, not silently covered by this result.
- limitations: strict historical weather availability/timezone remain unproven, not PASS. Live proof22fe637 reviewed with attribution to C2; no personal key transferred. GPU not claimed. Await frozenv2 before independent recomputation.
