"""Independent, read-only audit of frozen C2 evidence; never trains or loads .env.

Run from repository root with the optional research environment, supplying the
C2 working tree and a destination JSON. Only aggregate evidence is written.
"""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def score(y, p):
    d = np.asarray(p, dtype=float) - np.asarray(y, dtype=float)
    return dict(n=len(d), rmse=float(np.sqrt(np.dot(d, d) / len(d))),
                mae=float(np.sum(np.abs(d)) / len(d)), bias=float(d.sum() / len(d)))


def check_score(got, expected):
    for k in got:
        if not np.isclose(got[k], expected[k], rtol=0, atol=1e-12):
            raise ValueError(f"Metric mismatch {k}: {got[k]} vs {expected[k]}")


def dt(value):
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def bootstrap(frames, block_days=3):
    rng = np.random.default_rng(20260923)
    folds = []
    for rows in frames:
        days = sorted({r["valid_time"][:10] for r in rows})
        if any((datetime.fromisoformat(b) - datetime.fromisoformat(a)).days != 1
               for a, b in zip(days, days[1:])):
            raise ValueError("Missing calendar day; moving-block bootstrap needs calendar handling")
        daily = []
        for day in days:
            group = [r for r in rows if r["valid_time"][:10] == day]
            y = np.array([float(r["actual"]) for r in group])
            daily.append([np.sum((y - [float(r[p]) for r in group]) ** 2)
                          for p in ("ensemble", "curve")] + [len(group)])
        starts = rng.integers(len(days), size=(2000, (len(days) + block_days - 1) // block_days))
        indexes = ((starts[:, :, None] + np.arange(block_days)) % len(days)).reshape(2000, -1)[:, :len(days)]
        totals = np.array(daily)[indexes].sum(axis=1)
        folds.append(np.sqrt(totals[:, 0] / totals[:, 2]) - np.sqrt(totals[:, 1] / totals[:, 2]))
    return np.quantile(np.mean(folds, axis=0), [.025, .975]).tolist()


def main(c2, scada_dir, output):
    import torch
    from src.ml.deep_compare import make_model, infer
    torch.set_num_threads(2)
    c2 = Path(c2)
    published = Path("coordination/research/C2")
    dl = c2 / "artifacts/dl-v3"
    raw = read(dl / "results/report.json")
    data = np.load(dl / "pairs.npz", allow_pickle=False)
    if sha(dl / "pairs.npz") != raw["dataset_sha256"]:
        raise ValueError("Dataset SHA mismatch")
    if read(published / "evaluation-dl-v3.json") != raw:
        raise ValueError("Published DL report differs from local evidence")
    snapshot = read(published / "v2-snapshot.json")
    weather = {}
    for item in snapshot["files"]:
        source = c2 / "data/cache/v2-training" / (item["date"] + ".jsonl")
        if sha(source) != item["sha256"]:
            raise ValueError("Weather snapshot SHA mismatch")
        for line in source.read_text(encoding="utf-8-sig").splitlines():
            row = json.loads(line)
            weather[(item["date"] + "T12:00:00Z", row["valid_time"])] = row
    result = {"audit": "C5 independent recomputation", "training_performed": False,
              "snapshot_files_verified": len(snapshot["files"]), "dl_input_sha256": raw["dataset_sha256"],
              "dl_code_hash_matches": sha(c2 / "src/ml/deep_compare.py") == raw["code_sha256"],
              "auditor_code_equivalent_after_line_endings": Path("src/ml/deep_compare.py").read_text(encoding="utf-8") == (c2 / "src/ml/deep_compare.py").read_text(encoding="utf-8"),
              "january_comparison": {}, "dl": {}, "splits": {}, "error_slices": {}}
    if not result["dl_code_hash_matches"] or not result["auditor_code_equivalent_after_line_endings"]:
        raise ValueError("DL code no longer matches frozen report")
    for version, folder in (("v1", "evaluation"), ("v2-posttest", "evaluation-v2-posttest")):
        report = read(published / f"evaluation-{version}.json")
        result["january_comparison"][version] = {}
        for turbine, cell in report["turbines"].items():
            path = c2 / "artifacts" / folder / (turbine + "-test-predictions.csv")
            if sha(path) != cell["test_predictions_sha256"]:
                raise ValueError("January evidence hash mismatch")
            rows = list(csv.DictReader(path.open(encoding="utf-8")))
            models = {}
            for name in ("nwp_curve", "catboost"):
                groups = {"all_48": rows, "hours_1_24": [r for r in rows if int(r["lead_hours"]) <= 24],
                          "hours_25_48": [r for r in rows if int(r["lead_hours"]) > 24]}
                models[name] = {}
                for group, selected in groups.items():
                    got = score([float(r["actual"]) for r in selected], [float(r[name]) for r in selected])
                    check_score(got, cell["test"][name][group])
                    models[name][group] = got
            result["january_comparison"][version][turbine] = models
    summary = read(published / "dl-v3-summary.json")
    for turbine, families in raw["turbines"].items():
        x, y = data[turbine + "_x"], data[turbine + "_y"]
        valid, issue = data[turbine + "_valid"], data[turbine + "_issue"]
        pair_ids = list(zip(issue.tolist(), valid.tolist()))
        scada_path = Path(scada_dir) / f"scada-t{turbine[-1]}-hourly.jsonl"
        observation_rows = [json.loads(line) for line in scada_path.read_text(encoding="utf-8-sig").splitlines()]
        observations = {r["timestamp"]: r for r in observation_rows if r["coverage"] == 1 and not r["quality_flags"]}
        expected_features = []
        for origin, target in pair_ids:
            row = weather[(origin, target)]
            if dt(row["available_at"]) > dt(origin):
                raise ValueError("Weather violates assumed publication gate")
            v = row["variables"]
            direction = np.deg2rad(v["wind_direction_100m_deg"])
            clock = dt(target).hour * 2 * np.pi / 24
            expected_features.append([v["wind_speed_100m_m_s"], v["temperature_2m_c"], np.sin(direction), np.cos(direction), np.sin(clock), np.cos(clock), (dt(target)-dt(origin)).total_seconds()/3600])
        np.testing.assert_allclose(x, expected_features, rtol=0, atol=1e-12)
        np.testing.assert_array_equal(y, [observations[t]["power_normalized"] for t in valid])
        if len(set(pair_ids)) != len(pair_ids):
            raise ValueError("Duplicate issue/target pairs")
        if not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError("Nonfinite joined data")
        leads = np.array([(dt(v) - dt(i)).total_seconds() / 3600 for i, v in pair_ids])
        np.testing.assert_array_equal(leads, x[:, -1])
        if not ((leads >= 1) & (leads <= 48)).all():
            raise ValueError("Invalid forecast lead")
        result["dl"][turbine] = {}
        result["error_slices"][turbine] = {}
        split_results = {}
        for family, cells in families.items():
            frames, scores, checked_weights = [], [], 0
            for cutoff, cell in cells.items():
                tr = valid < cutoff
                va = (issue >= cutoff) & (valid < cell["end_exclusive"])
                if set(valid[tr]).intersection(valid[va]):
                    raise ValueError("Train/validation target overlap")
                if np.any(valid[va] >= "2026-01-01T00:00:00Z"):
                    raise ValueError("January labels in neural validation")
                inner = (dt(cutoff) - timedelta(days=14)).isoformat().replace("+00:00", "Z")
                inner_fit, inner_stop = valid < inner, (issue >= inner) & (valid < cutoff)
                if set(valid[inner_fit]).intersection(valid[inner_stop]):
                    raise ValueError("Inner stopping overlap")
                split_results[cutoff] = {"train_pairs": int(tr.sum()), "validation_pairs": int(va.sum()),
                                          "train_unique_targets": len(set(valid[tr])), "validation_unique_targets": len(set(valid[va])),
                                          "inner_train_pairs": int(inner_fit.sum()), "inner_stop_pairs": int(inner_stop.sum())}
                path = dl / "results" / f"{turbine}-{family}-{cutoff[:10]}-predictions.csv"
                if sha(path) != cell["predictions_sha256"]:
                    raise ValueError("DL prediction SHA mismatch")
                rows = list(csv.DictReader(path.open(encoding="utf-8")))
                if [(r["issue_time"], r["valid_time"]) for r in rows] != list(zip(issue[va], valid[va])):
                    raise ValueError("Prediction rows do not match temporal mask")
                np.testing.assert_array_equal([float(r["actual"]) for r in rows], y[va])
                got = score(y[va], [float(r["ensemble"]) for r in rows])
                check_score(got, cell["ensemble"]["all_48"])
                check_score(score(y[va], [float(r["curve"]) for r in rows]), cell["baseline"]["all_48"])
                if family == "residual_mlp":
                    vx = x[va]
                    slices = {}
                    for label, subset in (("wind_lt3", vx[:, 0] < 3), ("wind_3to8", (vx[:, 0] >= 3) & (vx[:, 0] < 8)),
                                          ("wind_ge8", vx[:, 0] >= 8), ("leads_1_24", vx[:, -1] <= 24), ("leads_25_48", vx[:, -1] > 24)):
                        slices[label] = {name: score(y[va][subset], np.array([float(r[name]) for r in rows])[subset])
                                         for name in ("curve", "ensemble")}
                    result["error_slices"][turbine][cutoff] = slices
                ensemble = np.mean([[float(r[f"seed_{s}"]) for r in rows] for s in raw["seeds"]], axis=0)
                np.testing.assert_allclose(ensemble, [float(r["ensemble"]) for r in rows], rtol=0, atol=1e-12)
                for seed in cell["seeds"]:
                    weight = dl / "results" / f"{turbine}-{family}-{cutoff[:10]}-{seed['seed']}.pt"
                    if sha(weight) != seed["weight_sha256"]:
                        raise ValueError("DL weight hash mismatch")
                    checkpoint = torch.load(weight, weights_only=True)
                    mean, scale = x[tr].mean(axis=0), x[tr].std(axis=0)
                    scale[scale < 1e-8] = 1
                    np.testing.assert_allclose(mean, checkpoint["mean"], rtol=0, atol=1e-12)
                    np.testing.assert_allclose(scale, checkpoint["scale"], rtol=0, atol=1e-12)
                    if checkpoint["fit_end_exclusive"] != cutoff:
                        raise ValueError("Checkpoint fit cutoff mismatch")
                    model = make_model(family, seed["seed"], "cpu")
                    model.load_state_dict(checkpoint["state_dict"])
                    tx = torch.tensor((x[va] - mean) / scale, dtype=torch.float32)
                    curve = checkpoint["curve"]
                    buckets = np.floor(x[tr, 0]).astype(int)
                    kept = [b for b in sorted(set(buckets)) if np.sum(buckets == b) >= 5]
                    np.testing.assert_allclose(curve["wind"], [x[tr, 0][buckets == b].mean() for b in kept], rtol=0, atol=1e-12)
                    np.testing.assert_allclose(curve["power"], [y[tr][buckets == b].mean() for b in kept], rtol=0, atol=1e-12)
                    predicted = np.interp(x[va, 0], curve["wind"], curve["power"]) + infer(model, tx)
                    np.testing.assert_allclose(predicted, [float(r[f"seed_{seed['seed']}"]) for r in rows], rtol=0, atol=2e-7)
                    checked_weights += 1
                frames.append(rows)
                scores.append(got["rmse"])
            interval = bootstrap(frames)
            np.testing.assert_allclose(interval, summary["turbines"][turbine]["details"][family]["descriptive_uncertainty"]["descriptive_95pct_interval"], rtol=0, atol=1e-12)
            result["dl"][turbine][family] = {"mean_fold_rmse": float(np.mean(scores)), "three_day_block_95pct": interval,
                                                 "five_day_block_95pct_sensitivity": bootstrap(frames, 5), "restored_weights": checked_weights,
                                                 "inference_tolerance": 2e-7}
        result["splits"][turbine] = split_results
    result["verified"] = True
    result["limitations"] = ["No February accuracy labels", "January already viewed: not a fresh test", "NWP publication +9h unconfirmed", "SCADA UTC+6 inferred", "December folds reused; intervals descriptive, not superiority certification"]
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"verified": True, "weather_hashes": len(snapshot["files"]), "weights_restored": 24, "output": str(output)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c2-root", required=True)
    parser.add_argument("--scada-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.c2_root, args.scada_dir, args.output)
