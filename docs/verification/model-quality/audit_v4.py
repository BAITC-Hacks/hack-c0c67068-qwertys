"""Independent frozen V4 audit. Reads existing outputs, never fits estimators."""
import argparse
import csv
from datetime import timedelta
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import hashlib

import numpy as np
import torch
from catboost import CatBoostRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from audit import check_score, dt, read, score, sha
from src.ml.deep_compare import make_model, infer

METHODS = ("curve", "curve_recent91", "catboost", "mlp_raw", "mlp_shrink")
FOLDS = [("2025-03-01", "2025-04-01"), ("2025-06-01", "2025-07-01"),
         ("2025-09-01", "2025-10-01"), ("2025-11-01", "2025-12-01"),
         ("2025-12-01", "2025-12-15"), ("2025-12-15", "2026-01-01")]


def iso(value):
    return value.isoformat().replace("+00:00", "Z")


def ramp_values(stamps, target):
    observations = {}
    for stamp, y in zip(stamps, target):
        if stamp in observations and observations[stamp] != y:
            raise ValueError("Conflicting repeated target")
        observations[stamp] = float(y)
    return np.array([abs(observations[s] - observations[iso(dt(s)-timedelta(hours=1))])
                     if iso(dt(s)-timedelta(hours=1)) in observations else np.nan for s in stamps])


def curve_fit_predict(x, y, wind):
    bins = np.floor(x).astype(int)
    kept = [k for k in sorted(set(bins)) if np.sum(bins == k) >= 5]
    centers = [x[bins == k].mean() for k in kept]
    powers = [y[bins == k].mean() for k in kept]
    return np.interp(wind, centers, powers)


def confidence(frames):
    rng = np.random.default_rng(20260923)
    distributions, missing_days = [], []
    for rows in frames:
        days = sorted({r["valid_time"][:10] for r in rows})
        absent = (dt(days[-1]) - dt(days[0])).days + 1 - len(days)
        missing_days.append(absent)
        sums = []
        for day in days:
            group = [r for r in rows if r["valid_time"][:10] == day]
            y = np.array([float(r["actual"]) for r in group])
            sums.append([np.sum((y - [float(r[m]) for r in group]) ** 2) for m in ("mlp_shrink", "curve")] + [len(group)])
        starts = rng.integers(len(days), size=(2000, (len(days)+2)//3))
        indexes = ((starts[:, :, None] + np.arange(3)) % len(days)).reshape(2000, -1)[:, :len(days)]
        totals = np.array(sums)[indexes].sum(axis=1)
        distributions.append(np.sqrt(totals[:, 0]/totals[:, 2])-np.sqrt(totals[:, 1]/totals[:, 2]))
    return np.quantile(np.mean(distributions, axis=0), [.025, .975]).tolist(), missing_days


def independent_gate(cells, interval):
    means = {m: float(np.mean([c["slices"]["all"][m]["rmse"] for c in cells])) for m in METHODS}
    failures = []
    for reference in ("curve", "curve_recent91", "catboost"):
        if means["mlp_shrink"] > .98 * means[reference]:
            failures.append(f"less than2percent mean RMSE gain vs {reference}")
    for c in cells:
        for name in ("all", "lead1_24", "lead25_48", "wind_ge8"):
            values = c["slices"].get(name)
            if not values or values["curve"]["n"] < 100:
                failures.append(c["cutoff"][:10]+": "+name+" insufficient evidence (<100pairs)")
                continue
            for reference in ("curve", "curve_recent91"):
                if values["mlp_shrink"]["rmse"] > 1.05*values[reference]["rmse"]:
                    failures.append(c["cutoff"][:10]+": "+name+f" >5percent RMSE regression vs {reference}")
        for reference in ("curve", "curve_recent91"):
            if abs(c["slices"]["all"]["mlp_shrink"]["bias"]) > abs(c["slices"]["all"][reference]["bias"])+.01:
                failures.append(c["cutoff"][:10]+f": absolute bias regression >.01 vs {reference}")
    if interval[1] >= 0:
        failures.append("descriptive delta interval upper endpoint is not negative")
    return {"eligible": not failures, "mean_fold_rmse": means, "failures": failures,
            "descriptive_95pct_block_interval_shrink_minus_curve": interval}


def main(c2, output):
    root = Path(c2)
    directory = root / "artifacts/dl-v4/gpu-export/quality-v4-results"
    archive = root / "artifacts/dl-v4/hackalem-quality-v4-results.zip"
    expected_sha = "908498c58a3c41d913a0258565e5f3c507200a2da5bd031373668de5cea3b67e"
    if sha(archive) != expected_sha:
        raise ValueError("V4 ZIP digest mismatch")
    with zipfile.ZipFile(archive) as z:
        members = [m for m in z.infolist() if not m.is_dir()]
        for member in members:
            path = (directory.parent / member.filename).resolve()
            if not path.is_relative_to(directory.parent.resolve()) or z.read(member) != path.read_bytes():
                raise ValueError("V4 archive/extraction mismatch")
    report = read(directory / "report.json")
    if report["status"] != "completed" or report["device"] != "cuda" or report["seeds"] != [42, 137, 2026]:
        raise ValueError("Incomplete or wrong-device V4 report")
    source = subprocess.check_output(["git", "show", "87de433:src/ml/quality_cycle.py"])
    if hashlib.sha256(source).hexdigest() != report["code_sha256"]:
        raise ValueError("Runtime code differs from frozen prefit V4 code")
    data_path = root / "artifacts/dl-v3/pairs.npz"
    if sha(data_path) != report["dataset_sha256"]:
        raise ValueError("Dataset differs from immutable audited V3 input")
    data = np.load(data_path, allow_pickle=False)
    torch.set_num_threads(2)
    result = {"archive_sha256": expected_sha, "archive_bytes": archive.stat().st_size, "archive_files_verified": len(members),
              "runtime_seconds": report["runtime_seconds"], "hardware_reported": report["hardware"],
              "weights_verified": 0, "catboost_models_verified": 0, "prediction_rows": 0, "slice_metric_sets_verified": 0,
              "max_cpu_replay_absolute_difference": 0.0, "max_catboost_restore_difference": 0.0, "turbines": {}}
    for turbine, entry in report["turbines"].items():
        x, y, valid, issue = [data[turbine + suffix] for suffix in ("_x", "_y", "_valid", "_issue")]
        cells = entry["folds"]
        if [(c["cutoff"][:10], c["end_exclusive"][:10]) for c in cells] != FOLDS:
            raise ValueError("Frozen six fold dates changed")
        frames = []
        for cell in cells:
            cutoff, end = cell["cutoff"], cell["end_exclusive"]
            fit, test = valid < cutoff, (issue >= cutoff) & (valid < end)
            recent = fit & (valid >= iso(dt(cutoff)-timedelta(days=91)))
            if np.any(valid[test] >= "2026-01-01T00:00:00Z") or set(valid[fit]).intersection(valid[test]):
                raise ValueError("January or overlapping outer targets")
            if cell["train_rows"] != fit.sum() or cell["test_rows"] != test.sum() or cell["status"] != "completed":
                raise ValueError("Fold status/count mismatch")
            path = directory / cell["prediction_file"]
            if sha(path) != cell["prediction_sha256"]:
                raise ValueError("V4 CSV digest mismatch")
            rows = list(csv.DictReader(path.open(encoding="utf-8")))
            if [(r["issue_time"], r["valid_time"]) for r in rows] != list(zip(issue[test], valid[test])):
                raise ValueError("V4 rows differ from temporal split")
            np.testing.assert_array_equal([float(r["actual"]) for r in rows], y[test])
            predictions = {m: np.array([float(r[m]) for r in rows]) for m in METHODS}
            if not all(np.isfinite(p).all() for p in predictions.values()):
                raise ValueError("Nonfinite V4 predictions")
            np.testing.assert_allclose(predictions["curve"], curve_fit_predict(x[fit, 0], y[fit], x[test, 0]), rtol=0, atol=1e-12)
            np.testing.assert_allclose(predictions["curve_recent91"], curve_fit_predict(x[recent, 0], y[recent], x[test, 0]), rtol=0, atol=1e-12)
            cb_path = directory / f"{turbine}-{cutoff[:10]}.cbm"
            if sha(cb_path) != cell["catboost_sha256"]:
                raise ValueError("CatBoost hash mismatch")
            cb = CatBoostRegressor(); cb.load_model(str(cb_path))
            cb_prediction = cb.predict(x[test])
            np.testing.assert_allclose(cb_prediction, predictions["catboost"], rtol=0, atol=1e-12)
            result["max_catboost_restore_difference"] = max(result["max_catboost_restore_difference"], float(np.max(np.abs(cb_prediction-predictions["catboost"]))))
            result["catboost_models_verified"] += 1
            if [s["seed"] for s in cell["seeds"]] != [42, 137, 2026]:
                raise ValueError("Missing or duplicated seeds")
            for seed in cell["seeds"]:
                weight = directory / seed["weight_file"]
                if sha(weight) != seed["weight_sha256"]:
                    raise ValueError("V4 weight digest mismatch")
                cp = torch.load(weight, map_location="cpu", weights_only=True)
                alpha = cp["alpha"]
                if not np.isfinite(alpha) or not 0 <= alpha <= 1 or alpha != seed["alpha"]:
                    raise ValueError("Invalid/mismatched alpha")
                if cp["fit_end_exclusive"] != cutoff or not cp["evaluation_only"]:
                    raise ValueError("V4 checkpoint role or cutoff mismatch")
                inner = iso(dt(cutoff)-timedelta(days=14))
                if seed["inner_cutoff"] != inner or seed["fit_rows"] != np.sum(valid < inner) or seed["stop_rows"] != np.sum((issue >= inner)&(valid < cutoff)):
                    raise ValueError("Inner alpha/epoch masks mismatch")
                best, selected = float("inf"), 1
                for point in seed["history"]:
                    if point["inner_rmse"] < best-report["config"]["min_delta"]:
                        best, selected = point["inner_rmse"], point["epoch"]
                if selected != seed["selected_epochs"]:
                    raise ValueError("Epoch choice differs from frozen stopping rule")
                mean, scale = x[fit].mean(axis=0), x[fit].std(axis=0)
                scale[scale < 1e-8] = 1
                np.testing.assert_allclose(cp["mean"], mean, rtol=0, atol=1e-12)
                np.testing.assert_allclose(cp["scale"], scale, rtol=0, atol=1e-12)
                model = make_model("residual_mlp", seed["seed"], "cpu"); model.load_state_dict(cp["state_dict"])
                residual = infer(model, torch.tensor((x[test]-mean)/scale, dtype=torch.float32))
                raw = np.array([float(r[f"raw_{seed['seed']}"]) for r in rows])
                shrink = np.array([float(r[f"shrink_{seed['seed']}"]) for r in rows])
                np.testing.assert_allclose(shrink, predictions["curve"]+alpha*(raw-predictions["curve"]), rtol=0, atol=1e-7)
                difference = float(np.max(np.abs(predictions["curve"]+residual-raw)))
                result["max_cpu_replay_absolute_difference"] = max(result["max_cpu_replay_absolute_difference"], difference)
                if not np.isfinite(residual).all():
                    raise ValueError("Nonfinite restored MLP")
                result["weights_verified"] += 1
            for output_name, prefix in (("mlp_raw", "raw"), ("mlp_shrink", "shrink")):
                np.testing.assert_allclose(predictions[output_name], np.mean([[float(r[f"{prefix}_{s}"]) for r in rows] for s in (42,137,2026)], axis=0), rtol=0, atol=1e-12)
            low, high = np.quantile(y[fit], [.1, .9])
            train_ramp = ramp_values(valid[fit], y[fit]); ramp90 = np.quantile(train_ramp[np.isfinite(train_ramp)], .9)
            for k, v in (("power_p10", low), ("power_p90", high), ("abs_hourly_ramp_p90", ramp90)):
                np.testing.assert_allclose(v, cell["slice_thresholds"][k], rtol=0, atol=1e-12)
            vx, vy = x[test], y[test]
            angle = np.mod(np.rad2deg(np.arctan2(vx[:,2], vx[:,3])), 360)
            masks = {"all": np.ones(len(vy), dtype=bool), "lead1_24": vx[:,-1]<=24, "lead25_48": vx[:,-1]>24,
                     "wind_lt4": vx[:,0]<4, "wind4_8": (vx[:,0]>=4)&(vx[:,0]<8), "wind_ge8": vx[:,0]>=8,
                     "temperature_lt0": vx[:,1]<0, "power_bottom10": vy<=low, "power_top10": vy>=high,
                     "ramp_top10": ramp_values(valid[test], vy)>=ramp90}
            masks.update({f"direction_q{i}": (angle>=90*i)&(angle<90*(i+1)) for i in range(4)})
            if set(cell["slices"]) != {name for name, mask in masks.items() if mask.any()}:
                raise ValueError("Missing or extra slice")
            for name, mask in masks.items():
                if mask.any():
                    for method in METHODS:
                        check_score(score(vy[mask], predictions[method][mask]), cell["slices"][name][method])
                        result["slice_metric_sets_verified"] += 1
            stamps, reverse = np.unique(valid[test], return_inverse=True); counts = np.bincount(reverse)
            actual = np.bincount(reverse, weights=vy)/counts
            for method in METHODS:
                averaged = np.bincount(reverse, weights=predictions[method])/counts
                check_score(score(actual, averaged), cell["unique_target_hour_average_predictions"][method])
            frames.append(rows)
            result["prediction_rows"] += len(rows)
        interval, gaps = confidence(frames)
        gate = independent_gate(cells, interval)
        if gate["eligible"] != entry["gate"]["eligible"] or gate["failures"] != entry["gate"]["failures"]:
            raise ValueError("Promotion gate differs from independent calculation")
        np.testing.assert_allclose(interval, entry["gate"]["descriptive_95pct_block_interval_shrink_minus_curve"], rtol=0, atol=1e-12)
        for method in METHODS:
            np.testing.assert_allclose(gate["mean_fold_rmse"][method], entry["gate"]["mean_fold_rmse"][method], rtol=0, atol=1e-12)
        result["turbines"][turbine] = {"gate": gate, "missing_calendar_days_in_bootstrap_folds": gaps}
    result["promotion_eligible"] = all(t["gate"]["eligible"] for t in result["turbines"].values())
    if result["promotion_eligible"] != report["quality_gate_passed"]:
        raise ValueError("Overall promotion flag mismatch")
    result["decision"] = "research-only; retain V1; stop model search"
    result["verified_scope"] = "independent hashes, data/splits, 36weights+12CBrestore, 12CSV metrics, CI and frozen gates; no fitting"
    result["alpha_limit"] = "Frozen source implements inner-only formula; stored alpha/masks/epoch choices/application checked. Inner-fit calibration predictions are not exported, so numerical alpha optimum cannot be independently recomputed without re-training. No such re-training performed."
    result["cross_device_note"] = "Maximum discrepancy reported, not a claim of bitwise equality across CPU/CUDA"
    restore_path = root / "artifacts/dl-v3/hackalem-cuda-restore.json"
    if restore_path.exists():
        result["v3_same_cuda_restore"] = {"file_sha256": sha(restore_path), "reported": read(restore_path),
                                          "evidence_level": "C2-produced local measurement JSON inspected; C5 did not run CUDA or independently reproduce this measurement; JSON does not bind per-weight hashes"}
    Path(output).write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c2-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.c2_root, args.output)
