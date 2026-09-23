"""Read-only GPU V3 export audit: hashes, metrics, bootstrap, CPU weight replay."""
import argparse
import contextlib
import csv
import io
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from audit import bootstrap, check_score, read, score, sha
from src.ml.deep_compare import infer, make_model
from src.ml.deep_report import summarize


def main(c2, output):
    root = Path(c2) / "artifacts/dl-v3"
    gpu = root / "gpu-export/gpu-results"
    cpu = read(root / "results/report.json")
    report = read(gpu / "report.json")
    archive = root / "hackalem-gpu-results.zip"
    with zipfile.ZipFile(archive) as z:
        members = [m for m in z.infolist() if not m.is_dir()]
        if len({Path(m.filename).name for m in members}) != len(members):
            raise ValueError("ZIP basename collision")
        for member in members:
            extracted = (gpu.parent / member.filename).resolve()
            if not extracted.is_relative_to(gpu.parent.resolve()):
                raise ValueError("Unsafe ZIP member path")
            if z.read(member) != extracted.read_bytes():
                raise ValueError("ZIP/extracted file mismatch")
    for name in ("experiment", "config", "seeds", "dataset_sha256", "code_sha256"):
        if cpu[name] != report[name]:
            raise ValueError(f"CPU/GPU protocol mismatch: {name}")
    if report["status"] != "completed" or report["device"] != "cuda":
        raise ValueError("GPU report is not completed CUDA")
    data = np.load(root / "pairs.npz", allow_pickle=False)
    if sha(root / "pairs.npz") != report["dataset_sha256"]:
        raise ValueError("GPU dataset hash mismatch")
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        summary = summarize(gpu, "coordination/research/C2/evaluation-v2-posttest.json", destination.with_name("gpu-verified-summary.json"))
    if summary != read(gpu / "summary.json"):
        raise ValueError("Exported GPU summary differs from recomputation")
    torch.set_num_threads(2)
    result = {"verified": False, "archive_sha256": sha(archive), "archive_bytes": archive.stat().st_size,
              "archive_files_verified": len(members), "reported_hardware": report["hardware"],
              "reported_device": report["device"], "reported_torch": report["torch_version"],
              "reported_platform": report["platform"], "runtime_seconds_gpu": report["runtime_seconds"],
              "runtime_seconds_cpu": cpu["runtime_seconds"], "same_protocol_and_data": True,
              "restored_weights": 0, "max_cpu_replay_absolute_difference": 0,
              "cross_device_comparison": "diagnostic only; same-CUDA restored inference is a separate pending check",
              "cross_device_differences": [], "turbines": {}}
    for turbine, families in report["turbines"].items():
        result["turbines"][turbine] = {}
        x, y = data[turbine + "_x"], data[turbine + "_y"]
        valid, issue = data[turbine + "_valid"], data[turbine + "_issue"]
        for family, cells in families.items():
            frames, scores = [], []
            for cutoff, cell in cells.items():
                reference = cpu["turbines"][turbine][family][cutoff]
                for field in ("train_rows", "validation_rows", "unique_train_hours", "unique_validation_hours", "end_exclusive"):
                    if cell[field] != reference[field]:
                        raise ValueError("CPU/GPU fold mismatch")
                va = (issue >= cutoff) & (valid < cell["end_exclusive"])
                tr = valid < cutoff
                rows = list(csv.DictReader((gpu / f"{turbine}-{family}-{cutoff[:10]}-predictions.csv").open(encoding="utf-8")))
                if [(r["issue_time"], r["valid_time"]) for r in rows] != list(zip(issue[va], valid[va])):
                    raise ValueError("GPU rows differ from expected temporal mask")
                np.testing.assert_array_equal([float(r["actual"]) for r in rows], y[va])
                for model, name in (("curve", "baseline"), ("ensemble", "ensemble")):
                    prediction = np.array([float(r[model]) for r in rows])
                    for group, mask in (("all_48", np.ones(va.sum(), dtype=bool)), ("hours_1_24", x[va, -1] <= 24), ("hours_25_48", x[va, -1] > 24)):
                        check_score(score(y[va][mask], prediction[mask]), cell[name][group])
                for seed in cell["seeds"]:
                    checkpoint = torch.load(gpu / f"{turbine}-{family}-{cutoff[:10]}-{seed['seed']}.pt", map_location="cpu", weights_only=True)
                    mean, scale = x[tr].mean(axis=0), x[tr].std(axis=0)
                    scale[scale < 1e-8] = 1
                    np.testing.assert_allclose(mean, checkpoint["mean"], rtol=0, atol=1e-12)
                    np.testing.assert_allclose(scale, checkpoint["scale"], rtol=0, atol=1e-12)
                    model = make_model(family, seed["seed"], "cpu")
                    model.load_state_dict(checkpoint["state_dict"])
                    curve = checkpoint["curve"]
                    prediction = np.interp(x[va, 0], curve["wind"], curve["power"]) + infer(model, torch.tensor((x[va] - mean) / scale, dtype=torch.float32))
                    expected = np.array([float(r[f"seed_{seed['seed']}"]) for r in rows])
                    check_score(score(y[va], expected), seed["validation"]["all_48"])
                    difference = float(np.max(np.abs(prediction - expected)))
                    result["max_cpu_replay_absolute_difference"] = max(result["max_cpu_replay_absolute_difference"], difference)
                    result["cross_device_differences"].append({"turbine": turbine, "family": family, "cutoff": cutoff,
                                                              "seed": seed["seed"], "max_absolute_difference": difference})
                    if not np.isfinite(prediction).all():
                        raise ValueError("Nonfinite CPU replay of GPU weights")
                    result["restored_weights"] += 1
                frames.append(rows)
                scores.append(cell["ensemble"]["all_48"]["rmse"])
            interval = bootstrap(frames)
            np.testing.assert_allclose(interval, summary["turbines"][turbine]["details"][family]["descriptive_uncertainty"]["descriptive_95pct_interval"], rtol=0, atol=1e-12)
            cpu_mean = float(np.mean([c["ensemble"]["all_48"]["rmse"] for c in cpu["turbines"][turbine][family].values()]))
            result["turbines"][turbine][family] = {"gpu_mean_fold_rmse": float(np.mean(scores)), "cpu_mean_fold_rmse": cpu_mean,
                                                 "gpu_minus_cpu": float(np.mean(scores)) - cpu_mean, "three_day_95pct_delta_vs_curve": interval}
    result["verified"] = True
    result["verified_scope"] = "archive/checkpoint/prediction integrity, exact metric and CI recomputation, same protocol/data; cross-device inference is diagnostic, not exact PASS"
    result["limitations"] = ["Different-device numerical results need not be bitwise equal", "GPU device identification comes from exported training report plus C2 runtime evidence, not a new C5 cloud query", "Reused temporal folds; all four intervals include zero", "NWP publication and SCADA timezone remain unconfirmed"]
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c2-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.c2_root, args.output)
