"""Frozen seasonal residual-shrinkage ablation; retrospective research only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import time
from datetime import timedelta
from pathlib import Path

import numpy as np
import torch
from catboost import CatBoostRegressor

from src.ml import deep_compare as dl
from src.ml.common import TURBINES, curve_predict, fit_curve, iso, metrics, utc, write_json
from src.ml.train import PARAMS

FOLDS = (
    ("2025-03-01T00:00:00Z", "2025-04-01T00:00:00Z"),
    ("2025-06-01T00:00:00Z", "2025-07-01T00:00:00Z"),
    ("2025-09-01T00:00:00Z", "2025-10-01T00:00:00Z"),
    ("2025-11-01T00:00:00Z", "2025-12-01T00:00:00Z"),
    *dl.FOLDS,
)
METHODS = ("curve", "curve_recent91", "catboost", "mlp_raw", "mlp_shrink")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_data(x, y, valid, issue):
    if x.shape != (len(y), 7) or valid.shape != y.shape or issue.shape != y.shape:
        raise ValueError("Invalid data dimensions")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Nonfinite data")
    if len(set(zip(issue, valid))) != len(y):
        raise ValueError("Duplicate issue/target pairs")
    if not all(i < v for i, v in zip(issue, valid)):
        raise ValueError("Targets must follow their issue")
    lead = np.array([(utc(v)-utc(i)).total_seconds()/3600 for i, v in zip(issue, valid)])
    if not np.array_equal(lead, x[:, -1]) or np.any((lead < 1) | (lead > 48)):
        raise ValueError("Invalid lead hours")


def alpha_fit(residual, target_residual):
    if not np.isfinite(residual).all() or not np.isfinite(target_residual).all():
        raise ValueError("Nonfinite calibration")
    energy = float(np.dot(residual, residual))
    return float(np.clip(np.dot(residual, target_residual) / energy, 0, 1)) if energy > 1e-12 else 0.0


def inner_calibration(seed, x, y, valid, issue, cutoff, device, deadline):
    count, detail = dl.select_epochs("residual_mlp", seed, x, y, valid, issue, cutoff, device, deadline)
    inner = detail["inner_cutoff"]
    fit = valid < inner
    stop = (issue >= inner) & (valid < cutoff)
    curve, mean, scale = dl.preprocessing(x[fit], y[fit])
    tx, ty = dl.tensor_data(x[fit], y[fit], curve, mean, scale, device)
    vx, _ = dl.tensor_data(x[stop], y[stop], curve, mean, scale, device)
    model = dl.make_model("residual_mlp", seed, device)
    optimizer = dl.optimizer_for(model)
    for _ in range(count):
        dl.epoch(model, optimizer, tx, ty, deadline)
    correction = dl.infer(model, vx)
    alpha = alpha_fit(correction, y[stop] - curve_predict(curve, x[stop, 0]))
    detail["alpha"] = alpha
    return count, alpha, detail


def ramps(valid, y):
    # One actual value per target hour, independent of overlapping NWP origins.
    values = {}
    for stamp, value in zip(valid, y):
        if stamp in values and not np.isclose(values[stamp], value, rtol=0, atol=1e-12):
            raise ValueError("Conflicting labels across origins")
        values[stamp] = float(value)
    return np.array([abs(values[s] - values[iso(utc(s)-timedelta(hours=1))])
                     if iso(utc(s)-timedelta(hours=1)) in values else np.nan for s in valid])


def slices(x, y, valid, train_y, train_ramps):
    low, high = np.quantile(train_y, [.1, .9])
    finite_ramps = train_ramps[np.isfinite(train_ramps)]
    ramp_threshold = float(np.quantile(finite_ramps, .9)) if len(finite_ramps) else None
    actual_ramps = ramps(valid, y)
    angle = np.mod(np.rad2deg(np.arctan2(x[:, 2], x[:, 3])), 360)
    result = {"all": np.ones(len(y), dtype=bool), "lead1_24": x[:, -1] <= 24,
              "lead25_48": x[:, -1] > 24, "wind_lt4": x[:, 0] < 4,
              "wind4_8": (x[:, 0] >= 4) & (x[:, 0] < 8), "wind_ge8": x[:, 0] >= 8,
              "temperature_lt0": x[:, 1] < 0, "power_bottom10": y <= low,
              "power_top10": y >= high,
              "ramp_top10": actual_ramps >= ramp_threshold if ramp_threshold is not None else np.zeros(len(y), dtype=bool)}
    result.update({f"direction_q{i}": (angle >= 90*i) & (angle < 90*(i+1)) for i in range(4)})
    return result, {"power_p10": float(low), "power_p90": float(high), "abs_hourly_ramp_p90": ramp_threshold}


def score_slices(y, predictions, masks):
    return {name: {method: metrics(y[mask], pred[mask]) for method, pred in predictions.items()}
            for name, mask in masks.items() if mask.any()}


def unique_hour_scores(valid, y, predictions):
    stamps, reverse = np.unique(valid, return_inverse=True)
    counts = np.bincount(reverse)
    actual = np.bincount(reverse, weights=y) / counts
    return {method: metrics(actual, np.bincount(reverse, weights=pred) / counts)
            for method, pred in predictions.items()}


def block_interval(cells, output, replicates=2000):
    rng = np.random.default_rng(20260923)
    fold_draws = []
    for cell in cells:
        path = output / cell["prediction_file"]
        if digest(path) != cell["prediction_sha256"]:
            raise ValueError("Prediction hash mismatch")
        with path.open(encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        days = sorted({r["valid_time"][:10] for r in rows})
        values = np.array([[sum((float(r["actual"])-float(r[method]))**2
                                   for r in rows if r["valid_time"].startswith(day))
                            for method in ("mlp_shrink", "curve")] +
                           [sum(r["valid_time"].startswith(day) for r in rows)] for day in days])
        starts = rng.integers(0, len(days), size=(replicates, (len(days)+2)//3))
        indexes = ((starts[..., None] + np.arange(3)) % len(days)).reshape(replicates, -1)[:, :len(days)]
        totals = values[indexes].sum(axis=1)
        fold_draws.append(np.sqrt(totals[:, 0]/totals[:, 2])-np.sqrt(totals[:, 1]/totals[:, 2]))
    return np.quantile(np.mean(fold_draws, axis=0), [.025, .975]).tolist()


def gate(cells, interval):
    complete = len(cells) == len(FOLDS) and all(c.get("status") == "completed" and
        [s["seed"] for s in c["seeds"]] == list(dl.SEEDS) for c in cells)
    if not complete:
        return {"eligible": False, "failures": ["incomplete six folds or seeds"]}
    means = {m: float(np.mean([c["slices"]["all"][m]["rmse"] for c in cells])) for m in METHODS}
    failures = []
    for ref in ("curve", "curve_recent91", "catboost"):
        if means["mlp_shrink"] > means[ref] * .98:
            failures.append(f"less than2percent mean RMSE gain vs {ref}")
    for c in cells:
        for name in ("all", "lead1_24", "lead25_48", "wind_ge8"):
            score = c["slices"].get(name)
            if score and (name == "all" or score["curve"]["n"] >= 100):
                if score["mlp_shrink"]["rmse"] > 1.05 * score["curve"]["rmse"]:
                    failures.append(c["cutoff"][:10] + ": " + name + " >5percent RMSE regression")
        if abs(c["slices"]["all"]["mlp_shrink"]["bias"]) > abs(c["slices"]["all"]["curve"]["bias"]) + .01:
            failures.append(c["cutoff"][:10] + ": absolute bias regression >.01")
    if interval is None or interval[1] >= 0:
        failures.append("descriptive delta interval upper endpoint is not negative")
    return {"eligible": not failures, "mean_fold_rmse": means, "failures": failures,
            "descriptive_95pct_block_interval_shrink_minus_curve": interval}


def run(dataset, output_dir, device, deadline):
    started = time.monotonic()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if (output / "report.json").exists():
        raise ValueError("Output already contains a run; preserve existing evidence")
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    data = np.load(dataset, allow_pickle=False)
    report = {"experiment": "post-test-quality-v4", "status": "running", "device": device,
              "hardware": torch.cuda.get_device_name() if device == "cuda" else platform.processor(),
              "torch_version": torch.__version__, "dataset_sha256": digest(dataset),
              "code_sha256": digest(__file__), "config": dl.CONFIG, "seeds": list(dl.SEEDS),
              "january_labels_used": False, "turbines": {}, "production_promoted": False}
    try:
        for turbine in TURBINES:
            keep = data[turbine+"_valid"] < "2026-01-01T00:00:00Z"
            x, y = data[turbine+"_x"][keep], data[turbine+"_y"][keep]
            valid, issue = data[turbine+"_valid"][keep], data[turbine+"_issue"][keep]
            validate_data(x, y, valid, issue)
            cells = report["turbines"].setdefault(turbine, {"folds": []})["folds"]
            for cutoff, end in FOLDS:
                dl.check_deadline(deadline)
                fit, test = valid < cutoff, (issue >= cutoff) & (valid < end)
                if min(fit.sum(), test.sum()) < 100:
                    raise ValueError("Insufficient outer fold coverage")
                curve, mean, scale = dl.preprocessing(x[fit], y[fit])
                recent = fit & (valid >= iso(utc(cutoff)-timedelta(days=91)))
                recent_curve = fit_curve(x[recent, 0], y[recent])
                predictions = {"curve": curve_predict(curve, x[test, 0]),
                               "curve_recent91": curve_predict(recent_curve, x[test, 0])}
                cell = {"cutoff": cutoff, "end_exclusive": end, "status": "running", "seeds": [],
                        "train_rows": int(fit.sum()), "test_rows": int(test.sum()),
                        "unique_train_hours": len(set(valid[fit])), "unique_test_hours": len(set(valid[test]))}
                cells.append(cell)
                cb = CatBoostRegressor(**{**PARAMS, "depth": 4, "task_type": "GPU" if device == "cuda" else "CPU"})
                cb.fit(x[fit], y[fit])
                predictions["catboost"] = cb.predict(x[test])
                cb_path = output / f"{turbine}-{cutoff[:10]}.cbm"
                cb.save_model(str(cb_path))
                cell["catboost_sha256"] = digest(cb_path)
                tx, ty = dl.tensor_data(x[fit], y[fit], curve, mean, scale, device)
                vx, _ = dl.tensor_data(x[test], y[test], curve, mean, scale, device)
                raw, shrunk = [], []
                for seed in dl.SEEDS:
                    tick = time.monotonic()
                    count, alpha, detail = inner_calibration(seed, x, y, valid, issue, cutoff, device, deadline)
                    model = dl.make_model("residual_mlp", seed, device)
                    optimizer = dl.optimizer_for(model)
                    for _ in range(count):
                        dl.epoch(model, optimizer, tx, ty, deadline)
                    correction = dl.infer(model, vx)
                    raw.append(predictions["curve"] + correction)
                    shrunk.append(predictions["curve"] + alpha*correction)
                    weights = output / f"{turbine}-{cutoff[:10]}-{seed}.pt"
                    torch.save({"state_dict": model.cpu().state_dict(), "family": "residual_mlp",
                                "mean": mean.tolist(), "scale": scale.tolist(), "curve": curve,
                                "alpha": alpha, "fit_end_exclusive": cutoff, "seed": seed,
                                "evaluation_only": True}, weights)
                    detail.update(seed=seed, weight_file=weights.name, weight_sha256=digest(weights),
                                  seconds=time.monotonic()-tick)
                    cell["seeds"].append(detail)
                    write_json(output / "report.json", report)
                    print(json.dumps({"turbine": turbine, "cutoff": cutoff, "seed": seed,
                                      "epochs": count, "alpha": alpha}), flush=True)
                predictions["mlp_raw"] = np.mean(raw, axis=0)
                predictions["mlp_shrink"] = np.mean(shrunk, axis=0)
                masks, thresholds = slices(x[test], y[test], valid[test], y[fit], ramps(valid[fit], y[fit]))
                cell["slice_thresholds"] = thresholds
                cell["slices"] = score_slices(y[test], predictions, masks)
                cell["unique_target_hour_average_predictions"] = unique_hour_scores(valid[test], y[test], predictions)
                path = output / f"{turbine}-{cutoff[:10]}-predictions.csv"
                with path.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.writer(stream)
                    writer.writerow(["issue_time", "valid_time", "actual", "wind", "lead", *METHODS,
                                     *[f"raw_{s}" for s in dl.SEEDS], *[f"shrink_{s}" for s in dl.SEEDS]])
                    writer.writerows(zip(issue[test], valid[test], y[test], x[test, 0], x[test, -1],
                                         *[predictions[m] for m in METHODS], *raw, *shrunk))
                cell.update(prediction_file=path.name, prediction_sha256=digest(path), status="completed")
                write_json(output / "report.json", report)
            interval = block_interval(cells, output)
            report["turbines"][turbine]["gate"] = gate(cells, interval)
        report["status"] = "completed"
        report["quality_gate_passed"] = all(t["gate"]["eligible"] for t in report["turbines"].values())
    except TimeoutError as error:
        report.update(status="deadline_reached", limitation=str(error), quality_gate_passed=False)
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, quality_gate_passed=False)
        raise
    finally:
        report["runtime_seconds"] = time.monotonic()-started
        write_json(output / "report.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--deadline", required=True)
    args = parser.parse_args()
    result = run(args.dataset, args.output_dir, args.device, utc(args.deadline).timestamp())
    print(json.dumps({"status": result["status"], "quality_gate_passed": result.get("quality_gate_passed"),
                      "runtime_seconds": result["runtime_seconds"]}))
