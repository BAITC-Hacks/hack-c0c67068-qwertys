"""Summarize frozen neural experiments and descriptive paired block uncertainty."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from src.ml.common import write_json


def verify_cell(directory, turbine, family, cutoff, cell, seeds):
    """Reject stale/corrupted evidence before presenting completed scores."""
    if tuple(seeds) != (42, 137, 2026) or sorted(s["seed"] for s in cell["seeds"]) != sorted(seeds):
        raise ValueError("Completed DL cell must contain all three frozen seeds exactly once")
    stem = f"{turbine}-{family}-{cutoff[:10]}"
    path = directory / f"{stem}-predictions.csv"
    if hashlib.sha256(path.read_bytes()).hexdigest() != cell["predictions_sha256"]:
        raise ValueError("DL prediction evidence SHA mismatch")
    for seed in cell["seeds"]:
        weight = directory / f"{stem}-{seed['seed']}.pt"
        if hashlib.sha256(weight.read_bytes()).hexdigest() != seed["weight_sha256"]:
            raise ValueError("DL checkpoint evidence SHA mismatch")
    with path.open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != cell["validation_rows"] or not rows:
        raise ValueError("DL prediction evidence row count mismatch")
    if len({(r["issue_time"], r["valid_time"]) for r in rows}) != len(rows):
        raise ValueError("Duplicate DL issue/target evidence")
    columns = ["actual", "curve", "ensemble", *[f"seed_{s}" for s in seeds]]
    values = np.array([[float(r[k]) for k in columns] for r in rows])
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite DL evidence")
    if not np.allclose(values[:, 2], values[:, 3:].mean(axis=1), rtol=0, atol=1e-12):
        raise ValueError("DL ensemble is not the mean of all frozen seeds")
    for index, name in ((1, "baseline"), (2, "ensemble")):
        residual = values[:, index] - values[:, 0]
        computed = {"n": len(rows), "rmse": np.sqrt(np.mean(residual ** 2)),
                    "mae": np.abs(residual).mean(), "bias": residual.mean()}
        reported = cell[name]["all_48"]
        if any(not np.isclose(value, reported[key], rtol=0, atol=1e-12)
               for key, value in computed.items()):
            raise ValueError("DL reported metrics differ from prediction evidence")
    return path


def uncertainty(paths, replicates=2000):
    """Pair residuals by target day, retaining repeated origins together.

    Circular moving blocks of three target days within each fold. This is
    exploratory uncertainty on reused December folds, not a fresh test or
    correction for architecture selection/multiple comparisons.
    """
    rng = np.random.default_rng(20260923)
    distributions = []
    for path in paths:
        with path.open(encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        days = sorted({r["valid_time"][:10] for r in rows})
        sums = []
        for day in days:
            group = [r for r in rows if r["valid_time"].startswith(day)]
            sums.append([sum((float(r["actual"]) - float(r[p])) ** 2 for r in group) for p in ("ensemble", "curve")] + [len(group)])
        values = np.array(sums)
        delta = []
        for _ in range(replicates):
            starts = rng.integers(0, len(days), size=(len(days) + 2) // 3)
            sampled = ((starts[:, None] + np.arange(3)) % len(days)).ravel()[:len(days)]
            totals = values[sampled].sum(axis=0)
            delta.append(float(np.sqrt(totals[0] / totals[2]) - np.sqrt(totals[1] / totals[2])))
        distributions.append(delta)
    means = np.mean(distributions, axis=0)
    return {"method": "2000 paired circular moving-block resamples; blocks of3target days, independently within each outer fold; mean fold RMSE difference neural minus curve",
            "descriptive_95pct_interval": np.quantile(means, [0.025, 0.975]).tolist(),
            "limitation": "Reused pretest folds; not a fresh generalization test or multiple-comparison-adjusted significance claim"}


def summarize(directory, comparison, destination):
    directory = Path(directory)
    raw = json.loads((directory / "report.json").read_text(encoding="utf-8"))
    v2 = json.loads(Path(comparison).read_text(encoding="utf-8"))
    result = {"status": raw["status"], "device": raw["device"], "runtime_seconds": raw.get("runtime_seconds"),
              "january_used": False, "dataset_sha256": raw["dataset_sha256"], "turbines": {}}
    for turbine, families in raw["turbines"].items():
        reference = v2["turbines"][turbine]["pretest_selection"]
        scores = {"curve": reference["mean_fold_rmse"]["nwp_curve"],
                  "catboost_depth4": reference["mean_fold_rmse"]["depth4_full"]}
        details = {}
        for family, cells in families.items():
            if len(cells) != 2 or not all(c["status"] == "completed" for c in cells.values()):
                details[family] = {"status": "incomplete"}
                continue
            paths = []
            for cutoff, cell in cells.items():
                expected = reference["folds"][cutoff]
                if cell["validation_rows"] != expected["validation_rows"]:
                    raise ValueError("DL and reference validation row counts differ")
                if abs(cell["baseline"]["all_48"]["rmse"] - expected["baseline"]["all_48"]["rmse"]) >= 1e-12:
                    raise ValueError("DL and reference baseline RMSE differ")
                paths.append(verify_cell(directory, turbine, family, cutoff, cell, raw["seeds"]))
            scores[family] = float(np.mean([c["ensemble"]["all_48"]["rmse"] for c in cells.values()]))
            details[family] = {"status": "completed", "ensemble_seeds": raw["seeds"],
                              "delta_vs_curve": scores[family] - scores["curve"],
                              "delta_vs_catboost": scores[family] - scores["catboost_depth4"],
                              "descriptive_uncertainty": uncertainty(paths)}
        result["turbines"][turbine] = {"mean_fold_rmse": scores, "details": details}
    write_json(destination, result)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--destination", required=True)
    args = parser.parse_args()
    summarize(args.directory, args.comparison, args.destination)
