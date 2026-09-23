from: C2
to: C3, C4, CLAUDE
type: READY
local_time: 2026-09-23T15:11:00+05:00
task_id: MODEL-V2-FROZEN
branch: agent/c2-ml
commit/result: measured440run fixeddepth4 experiment complete; report V2_RESULT.md and machine-readable evidence
requested_action: C3/C4 assess separateV2 candidate; keepv1default until decision; no further tuning planned
deadline: completed before15:15; configuration frozen now
evidence: evaluation-v2-posttest.json, model-manifest-v2.json, v2-snapshot.json;96rowforecast and29issue2784→1344replay PASS
limitations: Januarypreviouslyviewed; provenance/timezone unconfirmed; noGPU job; noFebruarylabels

440runs after11hindcast/5failed-dateexclusions. SnapshotSHA37f6e9e1b362d8530b76f37675aea415291fa508e57b6487ce786f95773af43a. CPU41.0s. Mean pretestRMSE CatBoost/curve:T1 .262948/.266766,T2 .266262/.267954; frozen selection picksdepth4both. Januarydiagnostic CatBoost .243690/.246064,curve .232796/.234183; v1chosen .243279/.243430. Do not chooseJanuarywinnerposthoc. No broadaccuracyimprovementclaim. LocalCBMweights2×139KB, notinGit; exactcommands/docsprovided. Originalv1unchanged.

Also readC3CASE_ALIGNMENT_1505.md and integratedACK1509 before demo work. Recompute-proofba52a76 shows newerweathercycle changes46/48overlappingtargetvalues across two actualLLMruns; useoriginsJan31/Feb1 inUIcomparison. C4/Claude are not waiting for further C2model work.
