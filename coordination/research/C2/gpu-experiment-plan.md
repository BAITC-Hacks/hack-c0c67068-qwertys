# GPU hardware reproduction — frozen plan

Prepared before GPU execution on2026-09-23. GPU is NOT yet running.

- One Brev/AWSg4dn.xlarge:1×T4,16GBVRAM,16GiBRAM,4CPU,128GiBdisk. UI quote$0.63/hcompute+$0.02/hstorage=$0.65/h. Balance$50. Stop within30minutes of deploy; then check remainingdiskbill separately. Deployment may take7minutes.
- Name hackalem-c2-gpu. VM+Jupyter, setup creates privatevenv with numpy2.5.3,catboost1.2.10 and clones repo pinned tod7d8a68. Sourcecodeversion fixed in preparedsetup.
- Initial privateinput `artifacts/gpu-input/pairs.npz`,115951bytes,SHA94d90c8150e4499c2b1e388e31658366918c9ca973a2df551d05abf60966704a. It is excluded fromGit. Upload only to this authorizedGPU after provider consent. No API key needed onGPU and none will be transferred.
- `python -m src.ml.gpu_compare --dataset <pairs.npz> --task-type GPU --output-dir artifacts/gpu-comparison`. Same frozen depth4candidate,400iterations,lr0.04,seed42,two pretestfolds then Januaryreproduction. CPU command identical except--task-typeCPU, already1.594s total. GPUreport must include actual nvidia-smi/device,version,datasetSHA,fit times,per-turbine/per-lead metrics,artifactSHA.
- No production promotion based onGPUbrand or previously openedJanuarytest. Productionv1 retains windcurve selected beforetest. Januaryscores here are explicitly a post-testhardware reproduction.
- Fetch report and modelartifacts before shutdown. No more than onepaidinstance. Ifsetupfails/capacityunavailable within10minutes,stop and keepCPU result.

Separateyearlongpretestdata request toC1 has hardstop15:08, separatecache andV2post-testlabel. Do not overwritev1 while C4accepts it. Any later longhistoryexperiment uses same fixedpretestselectionprotocol and explicit disclosure ofalready-openedJanuarytest.
