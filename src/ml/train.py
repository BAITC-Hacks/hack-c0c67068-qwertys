"""Reproduce chronological baseline/CatBoost comparison and a pre-February model."""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.metadata
import json
import time
from datetime import timedelta
from pathlib import Path
import numpy as np
from src.ml.common import FEATURES, TURBINES, curve_predict, features, fingerprint, fit_curve, iso, metrics, read_jsonl, utc, write_json
from src.weather.open_meteo import select_horizon

PARAMS = dict(iterations=400, depth=5, learning_rate=0.04, loss_function="RMSE", random_seed=42, thread_count=4, verbose=False, allow_writing_files=False)
CANDIDATES = {"depth4_full": {"depth":4,"feature_mask":[1]*7}, "depth5_full": {"depth":5,"feature_mask":[1]*7}, "depth5_no_direction_clock": {"depth":5,"feature_mask":[1,1,0,0,0,0,1]}}
TRAIN_END = "2025-12-15T00:00:00Z"
VALID_END = "2026-01-01T00:00:00Z"
FINAL_END = "2026-01-31T00:00:00Z"


def observations(directory):
    result = {}
    for number, turbine in enumerate(TURBINES, start=1):
        rows = read_jsonl(Path(directory)/f"scada-t{number}-hourly.jsonl")
        result[turbine] = {row["timestamp"]: row for row in rows if row["coverage"] == 1 and not row["quality_flags"]}
    return result


def prepare_pairs(obs, weather_dir):
    pairs = {t: [] for t in TURBINES}
    sources = set()
    for path in sorted(Path(weather_dir).glob("????-??-??.jsonl")):
        rows = read_jsonl(path)
        if not rows:
            continue
        issue = utc(rows[0]["run_time"]) + timedelta(hours=12)
        if issue >= utc(FINAL_END):
            continue
        rows = select_horizon(rows, iso(issue), 48)
        x = features(rows, issue)
        sources.add(rows[0]["source_reference"])
        for turbine in TURBINES:
            past = [r for stamp, r in obs[turbine].items() if utc(stamp)+timedelta(hours=1) <= issue]
            recent = max(past, key=lambda r:r["timestamp"]) if past else None
            # Persistence exists only for a fully measured hour no older than 24h.
            persistence = recent["power_normalized"] if recent and issue-utc(recent["timestamp"]) <= timedelta(hours=24) else None
            for w, feature in zip(rows, x):
                label = obs[turbine].get(w["valid_time"])
                if label and utc(w["valid_time"]) < utc(FINAL_END):
                    pairs[turbine].append({"x": feature.tolist(), "y": label["power_normalized"], "valid_time": w["valid_time"], "issue_time": iso(issue), "persistence": persistence})
    return pairs, sorted(sources)


def fit_models(rows, config=None):
    from catboost import CatBoostRegressor
    x = np.array([r["x"] for r in rows]); y = np.array([r["y"] for r in rows])
    curve = fit_curve(x[:, 0], y)
    config=config or CANDIDATES["depth5_full"]
    candidate = CatBoostRegressor(**{**PARAMS,"depth":config["depth"]})
    candidate.fit(x*np.array(config["feature_mask"]), y)
    candidate.set_feature_names(FEATURES)
    return curve, candidate


def compare(rows, curve, candidate, mask=None):
    x = np.array([r["x"] for r in rows]); y = np.array([r["y"] for r in rows])
    predictions = {"nwp_curve": curve_predict(curve, x[:, 0]), "catboost": candidate.predict(x*np.array(mask or [1]*7))}
    result = {name: {"all_48": metrics(y,p), "hours_1_24": metrics(y[x[:,-1]<=24],p[x[:,-1]<=24]), "hours_25_48": metrics(y[x[:,-1]>24],p[x[:,-1]>24])} for name,p in predictions.items()}
    mask = np.array([r["persistence"] is not None for r in rows])
    if mask.any():
        result["persistence"] = {"available_only": metrics(y[mask],[r["persistence"] for r in rows if r["persistence"] is not None]), "coverage": float(mask.mean())}
    return result


def select_pretest(rows, candidates=None):
    """Two expanding pretest folds; January never participates in selection."""
    folds=[("2025-12-01T00:00:00Z",TRAIN_END),(TRAIN_END,VALID_END)]
    candidates=candidates or CANDIDATES
    details={}; scores={name:[] for name in ["nwp_curve",*candidates]}
    for start,end in folds:
        training=[r for r in rows if utc(r["valid_time"])<utc(start)]
        validation=[r for r in rows if utc(r["issue_time"])>=utc(start) and utc(r["valid_time"])<utc(end)]
        if min(len(training),len(validation))<100: raise ValueError("Insufficient pretest fold coverage")
        trial_results={}
        for name,config in candidates.items():
            curve,model=fit_models(training,config)
            train_result=compare(training,curve,model,config["feature_mask"])
            val_result=compare(validation,curve,model,config["feature_mask"])
            trial_results[name]={"train":train_result["catboost"],"validation":val_result["catboost"]}
            scores[name].append(val_result["catboost"]["all_48"]["rmse"])
        scores["nwp_curve"].append(val_result["nwp_curve"]["all_48"]["rmse"])
        details[start]={"end_exclusive":end,"train_rows":len(training),"validation_rows":len(validation),"baseline":val_result["nwp_curve"],"trials":trial_results}
    means={name:float(np.mean(values)) for name,values in scores.items()}
    selected=min(means,key=means.get)
    best_candidate=min(candidates,key=lambda name:means[name])
    return selected,best_candidate,{"folds":details,"mean_fold_rmse":means,"selection":"lowest unweighted mean of two fold RMSEs; ties preserve insertion-order baseline"}


def train(scada_dir, weather_dir, output_dir, report_path, baseline_only=False, fixed_candidate=None, experiment_label="v1-pretest-selection"):
    started=time.monotonic(); obs=observations(scada_dir); output=Path(output_dir); output.mkdir(parents=True,exist_ok=True)
    manifest={"training_end_exclusive": FINAL_END, "scada_timezone":"fixed UTC+6 hypothesis", "features":FEATURES, "turbines":{}}
    report={"unit":"normalized_power", "target_split":{"train_end_exclusive":TRAIN_END,"validation_end_exclusive":VALID_END,"test_end_exclusive":FINAL_END}, "protocol":"Split by target timestamp AND issue_time>=fit cutoff for evaluation; preserve overlapping issues, each issue/target pair has weight 1. Select on two pre-January expanding folds; freeze before January test. Complete SCADA hours only. Historical NWP availability conditional (+9h). Bias=mean(prediction-actual). No capacity normalization.", "params":PARAMS,"candidate_grid":CANDIDATES,"versions":{name:importlib.metadata.version(name) for name in ("numpy","pandas","catboost")},"scada_input_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(scada_dir).glob("scada-t*-hourly.jsonl")}, "turbines":{}, "february_metrics":None}
    candidates={fixed_candidate:CANDIDATES[fixed_candidate]} if fixed_candidate else CANDIDATES
    report["candidate_grid"]=candidates
    report["experiment_label"]=experiment_label
    report["january_test_previously_viewed"]=experiment_label.startswith("post-test")
    if baseline_only:
        for turbine in TURBINES:
            rows=[r for stamp,r in obs[turbine].items() if utc(stamp)<utc(FINAL_END)]
            curve=fit_curve([r["wind_m_s"] for r in rows],[r["power_normalized"] for r in rows])
            manifest["turbines"][turbine]={"kind":"curve","curve":curve}
            report["turbines"][turbine]={"train_hours":len(rows),"limitation":"SCADA wind→power applied to NWP 100m wind; uncalibrated domain shift, emergency baseline only"}
        manifest["model_version"]="scada-curve-"+fingerprint(manifest)[:12]
    else:
        pairs,sources=prepare_pairs(obs,weather_dir); report["weather_source_sha256"]=sources
        for turbine,rows in pairs.items():
            tr=[r for r in rows if utc(r["valid_time"])<utc(TRAIN_END)]
            va=[r for r in rows if utc(r["issue_time"])>=utc(TRAIN_END) and utc(r["valid_time"])<utc(VALID_END)]
            te=[r for r in rows if utc(r["issue_time"])>=utc(VALID_END) and utc(r["valid_time"])<utc(FINAL_END)]
            if min(len(tr),len(va),len(te))<100:
                raise ValueError("Insufficient temporal split coverage")
            selected,best_candidate,selection=select_pretest(rows,candidates)
            config=CANDIDATES[best_candidate]
            curve,candidate=fit_models(tr,config)
            validation=compare(va,curve,candidate,config["feature_mask"])
            # Refit on train+validation only, test remains untouched by fitting/selection.
            pretest=[r for r in rows if utc(r["valid_time"])<utc(VALID_END)]
            curve_test,candidate_test=fit_models(pretest,config)
            test=compare(te,curve_test,candidate_test,config["feature_mask"])
            evidence_path=Path(report_path).parent/(turbine+"-test-predictions.csv")
            evidence_path.parent.mkdir(parents=True,exist_ok=True)
            tx=np.array([r["x"] for r in te]); baseline_pred=curve_predict(curve_test,tx[:,0]); candidate_pred=candidate_test.predict(tx*np.array(config["feature_mask"]))
            with evidence_path.open("w",encoding="utf-8",newline="") as stream:
                writer=csv.DictWriter(stream,fieldnames=["turbine_id","issue_time","valid_time","lead_hours","actual","nwp_curve","catboost","persistence"]); writer.writeheader()
                for row,b,c in zip(te,baseline_pred,candidate_pred): writer.writerow({"turbine_id":turbine,"issue_time":row["issue_time"],"valid_time":row["valid_time"],"lead_hours":int(row["x"][-1]),"actual":row["y"],"nwp_curve":float(b),"catboost":float(c),"persistence":row["persistence"]})
            curve_final,candidate_final=fit_models(rows,config)
            if selected!="nwp_curve":
                filename=f"{turbine}.cbm"; candidate_final.save_model(str(output/filename))
                manifest["turbines"][turbine]={"kind":"catboost","file":filename,"feature_mask":config["feature_mask"],"sha256":hashlib.sha256((output/filename).read_bytes()).hexdigest()}
            else:
                manifest["turbines"][turbine]={"kind":"curve","curve":curve_final}
            possible_test_hours=sum(1 for path in Path(weather_dir).glob("????-??-??.jsonl") for r in read_jsonl(path) if utc(r["run_time"])+timedelta(hours=12)>=utc(VALID_END) and utc(r["run_time"])+timedelta(hours=12)<utc(FINAL_END) and utc(r["valid_time"])<utc(FINAL_END))
            report["turbines"][turbine]={"selected_on_validation":selected,"candidate_config":config,"pretest_selection":selection,"counts":{"train":len(tr),"validation":len(va),"test":len(te)},"test_coverage":{"labelled_pairs":len(te),"possible_pairs":possible_test_hours,"coverage":len(te)/possible_test_hours,"missing_pairs":possible_test_hours-len(te)},"unique_target_hours":{"train":len({r['valid_time'] for r in tr}),"validation":len({r['valid_time'] for r in va}),"test":len({r['valid_time'] for r in te})},"validation":validation,"test":test,"test_predictions_sha256":hashlib.sha256(evidence_path.read_bytes()).hexdigest(),"candidate_rmse_delta":test["catboost"]["all_48"]["rmse"]-test["nwp_curve"]["all_48"]["rmse"]}
        manifest["model_version"]="nwp-tabular-"+fingerprint({"params":PARAMS,"sources":sources,"results":report["turbines"]})[:12]
    report["evaluation_fit_end_exclusive"]=VALID_END
    report["production_fit_end_exclusive"]=FINAL_END
    report["estimator_relationship"]="January metrics belong to estimators fitted only on pre-January targets. model_version identifies final production refit, not the January-test estimator. Same family/configuration, different fitted parameters."
    report["runtime_seconds"]=round(time.monotonic()-started,3); report["model_version"]=manifest["model_version"]
    write_json(output/"manifest.json",manifest); write_json(report_path,report)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scada-dir",required=True,type=Path)
    parser.add_argument("--weather-dir",type=Path)
    parser.add_argument("--output-dir",type=Path,default=Path("models/production"))
    parser.add_argument("--report",type=Path,default=Path("artifacts/evaluation.json"))
    parser.add_argument("--baseline-only",action="store_true")
    parser.add_argument("--fixed-candidate",choices=list(CANDIDATES),help="Run just the frozen named candidate versus baseline; no configuration search")
    parser.add_argument("--experiment-label",default="v1-pretest-selection")
    args=parser.parse_args()
    if not args.baseline_only and args.weather_dir is None: parser.error("--weather-dir required for candidate")
    report=train(args.scada_dir,args.weather_dir,args.output_dir,args.report,args.baseline_only,args.fixed_candidate,args.experiment_label)
    print(json.dumps({"model_version":report["model_version"],"runtime_seconds":report["runtime_seconds"],"report":str(args.report)}))

if __name__=="__main__": main()
