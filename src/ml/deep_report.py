"""Summarize frozen neural experiments and descriptive paired block uncertainty."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from src.ml.common import write_json


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
            for cutoff, cell in cells.items():
                expected = reference["folds"][cutoff]
                assert cell["validation_rows"] == expected["validation_rows"]
                assert abs(cell["baseline"]["all_48"]["rmse"] - expected["baseline"]["all_48"]["rmse"]) < 1e-12
            scores[family] = float(np.mean([c["ensemble"]["all_48"]["rmse"] for c in cells.values()]))
            paths = [directory / f"{turbine}-{family}-{cutoff[:10]}-predictions.csv" for cutoff in cells]
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
