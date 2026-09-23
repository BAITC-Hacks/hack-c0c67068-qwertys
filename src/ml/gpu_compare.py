"""Hardware reproduction of frozen depth-4 candidate; not a new untouched test.

Prepare a compact private NPZ locally, transfer only to the authorized GPU,
then run identical commands with --task-type CPU/GPU. No model reselection.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import time
from pathlib import Path
import numpy as np
from src.ml.common import TURBINES, metrics, write_json
from src.ml.train import observations,prepare_pairs,PARAMS


def prepare(scada_dir,weather_dir,dataset):
    pairs,sources=prepare_pairs(observations(scada_dir),weather_dir)
    data={}
    for turbine,rows in pairs.items():
        data[turbine+"_x"]=np.array([r["x"] for r in rows],dtype=np.float64)
        data[turbine+"_y"]=np.array([r["y"] for r in rows],dtype=np.float64)
        data[turbine+"_valid"]=np.array([r["valid_time"] for r in rows])
        data[turbine+"_issue"]=np.array([r["issue_time"] for r in rows])
    dataset=Path(dataset); dataset.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(dataset,**data)
    write_json(dataset.with_suffix(".json"),{"sha256":hashlib.sha256(dataset.read_bytes()).hexdigest(),"bytes":dataset.stat().st_size,"weather_sources":sources,"purpose":"Private authorized NVIDIA GPU training input, excluded from Git","features":"same as model v1","params":{**PARAMS,"depth":4},"selection_frozen":"NWP curve remains chosen production model; this compares hardware for the existing candidate"})


def compare(dataset,task_type,output_dir):
    from catboost import CatBoostRegressor
    started=time.monotonic(); output=Path(output_dir); output.mkdir(parents=True,exist_ok=True)
    hardware=None
    if task_type=="GPU":
        hardware=subprocess.check_output(["nvidia-smi","--query-gpu=name,memory.total,driver_version","--format=csv,noheader"],text=True,timeout=10).strip()
    data=np.load(dataset,allow_pickle=False)
    report={"task_type":task_type,"gpu":hardware,"platform":platform.platform(),"versions":{p:importlib.metadata.version(p) for p in ("catboost","numpy")},"dataset_sha256":hashlib.sha256(Path(dataset).read_bytes()).hexdigest(),"params":{**PARAMS,"depth":4,"task_type":task_type},"status":"hardware reproduction after January test was opened; no selection or new test claim","turbines":{}}
    for turbine in TURBINES:
        x=data[turbine+"_x"]; y=data[turbine+"_y"]; valid=data[turbine+"_valid"]; issue=data[turbine+"_issue"]
        results={}
        for cutoff,end in (("2025-12-01T00:00:00Z","2025-12-15T00:00:00Z"),("2025-12-15T00:00:00Z","2026-01-01T00:00:00Z"),("2026-01-01T00:00:00Z","2026-01-31T00:00:00Z")):
            tr=valid<cutoff; va=(issue>=cutoff)&(valid<end)
            params={**PARAMS,"depth":4,"task_type":task_type}
            if task_type=="GPU": params["devices"]="0"
            model=CatBoostRegressor(**params); fit_start=time.monotonic(); model.fit(x[tr],y[tr]); elapsed=time.monotonic()-fit_start
            prediction=model.predict(x[va]); lead=x[va,-1]
            results[cutoff]={"fit_seconds":elapsed,"train_rows":int(tr.sum()),"test_rows":int(va.sum()),"train":metrics(y[tr],model.predict(x[tr])),"all_48":metrics(y[va],prediction),"hours_1_24":metrics(y[va][lead<=24],prediction[lead<=24]),"hours_25_48":metrics(y[va][lead>24],prediction[lead>24])}
            if cutoff.startswith("2026-01"):
                artifact=output/(turbine+"-candidate.cbm"); model.save_model(str(artifact)); results[cutoff]["artifact_sha256"]=hashlib.sha256(artifact.read_bytes()).hexdigest()
        report["turbines"][turbine]=results
    report["total_seconds"]=time.monotonic()-started
    write_json(output/"report.json",report)
    print(json.dumps(report,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare",action="store_true")
    parser.add_argument("--scada-dir"); parser.add_argument("--weather-dir")
    parser.add_argument("--dataset",type=Path,default=Path("artifacts/gpu-input/pairs.npz"))
    parser.add_argument("--task-type",choices=("CPU","GPU"),default="GPU")
    parser.add_argument("--output-dir",default="artifacts/gpu-comparison")
    args=parser.parse_args()
    if args.prepare: prepare(args.scada_dir,args.weather_dir,args.dataset)
    else: compare(args.dataset,args.task_type,args.output_dir)

if __name__=="__main__": main()
