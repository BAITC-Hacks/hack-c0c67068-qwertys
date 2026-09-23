"""Bounded, nested chronological DL comparison; optional PyTorch research tool.

See coordination/research/C2/DL_V3_PROTOCOL.md. Never reads January labels.
"""
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
from torch import nn

from src.ml.common import TURBINES, curve_predict, fit_curve, iso, metrics, utc, write_json

SEEDS = (42, 137, 2026)
FOLDS = (("2025-12-01T00:00:00Z", "2025-12-15T00:00:00Z"),
         ("2025-12-15T00:00:00Z", "2026-01-01T00:00:00Z"))
CONFIG = dict(batch_size=512, max_epochs=60, patience=8, min_delta=0.0001,
              lr=0.001, weight_decay=0.001, gradient_norm=1.0, dropout=0.1)


class ResidualBlock(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.net = nn.Sequential(nn.LayerNorm(width), nn.Linear(width, width),
                                 nn.GELU(), nn.Dropout(0.1), nn.Linear(width, width),
                                 nn.Dropout(0.1))

    def forward(self, x):
        return x + self.net(x)


class ResidualMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(7, 64), nn.GELU(),
                                 *[ResidualBlock(64) for _ in range(3)],
                                 nn.LayerNorm(64), nn.Linear(64, 1))
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(self, x):
        return self.net(x).squeeze(-1)


class FeatureTransformer(nn.Module):
    """Small numerical-token attention model, not an exact FT-Transformer clone."""
    def __init__(self):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(7, 32) * 0.02)
        self.bias = nn.Parameter(torch.randn(7, 32) * 0.02)
        self.cls = nn.Parameter(torch.randn(1, 1, 32) * 0.02)
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(32, 4, dim_feedforward=64, dropout=0.1,
                                       activation="gelu", batch_first=True, norm_first=True)
            for _ in range(3)])
        self.norm = nn.LayerNorm(32)
        self.head = nn.Linear(32, 1)
        nn.init.zeros_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(self, x):
        tokens = x.unsqueeze(-1) * self.weight + self.bias
        tokens = torch.cat((self.cls.expand(len(x), -1, -1), tokens), dim=1)
        for layer in self.layers:
            tokens = layer(tokens)
        return self.head(self.norm(tokens[:, 0])).squeeze(-1)


def make_model(name, seed, device):
    torch.manual_seed(seed)
    if device.startswith("cuda"):
        torch.cuda.manual_seed_all(seed)
    return (ResidualMLP() if name == "residual_mlp" else FeatureTransformer()).to(device)


def check_deadline(deadline):
    if time.time() >= deadline:
        raise TimeoutError("Frozen DL wall-clock deadline reached")


def preprocessing(x, y):
    curve = fit_curve(x[:, 0], y)
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale < 1e-8] = 1.0
    return curve, mean, scale


def tensor_data(x, y, curve, mean, scale, device):
    tx = torch.tensor((x - mean) / scale, dtype=torch.float32, device=device)
    residual = y - curve_predict(curve, x[:, 0])
    return tx, torch.tensor(residual, dtype=torch.float32, device=device)


def infer(model, x):
    model.eval()
    with torch.inference_mode():
        return torch.cat([model(batch) for batch in x.split(1024)]).cpu().numpy()


def epoch(model, optimizer, x, y, deadline):
    check_deadline(deadline)
    model.train()
    order = torch.randperm(len(x), device=x.device)
    for batch in order.split(CONFIG["batch_size"]):
        check_deadline(deadline)
        optimizer.zero_grad(set_to_none=True)
        loss = nn.functional.mse_loss(model(x[batch]), y[batch])
        if not torch.isfinite(loss):
            raise ValueError("Non-finite training loss")
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), CONFIG["gradient_norm"])
        optimizer.step()


def optimizer_for(model):
    return torch.optim.AdamW(model.parameters(), lr=CONFIG["lr"],
                             weight_decay=CONFIG["weight_decay"])


def select_epochs(name, seed, x, y, valid, issue, cutoff, device, deadline):
    inner = iso(utc(cutoff) - timedelta(days=14))
    fit = valid < inner
    stop = (issue >= inner) & (valid < cutoff)
    if min(fit.sum(), stop.sum()) < 100:
        raise ValueError("Insufficient inner temporal coverage")
    curve, mean, scale = preprocessing(x[fit], y[fit])
    tx, ty = tensor_data(x[fit], y[fit], curve, mean, scale, device)
    vx, _ = tensor_data(x[stop], y[stop], curve, mean, scale, device)
    base = curve_predict(curve, x[stop, 0])
    model = make_model(name, seed, device)
    optimizer = optimizer_for(model)
    best, best_epoch, stale = float("inf"), 1, 0
    history = []
    for number in range(1, CONFIG["max_epochs"] + 1):
        epoch(model, optimizer, tx, ty, deadline)
        score = metrics(y[stop], base + infer(model, vx))["rmse"]
        history.append({"epoch": number, "inner_rmse": score})
        if score < best - CONFIG["min_delta"]:
            best, best_epoch, stale = score, number, 0
        else:
            stale += 1
        if stale >= CONFIG["patience"]:
            break
    return best_epoch, {"inner_cutoff": inner, "fit_rows": int(fit.sum()),
                        "stop_rows": int(stop.sum()), "selected_epochs": best_epoch,
                        "history": history}


def lead_metrics(y, prediction, x):
    return {"all_48": metrics(y, prediction),
            "hours_1_24": metrics(y[x[:, -1] <= 24], prediction[x[:, -1] <= 24]),
            "hours_25_48": metrics(y[x[:, -1] > 24], prediction[x[:, -1] > 24])}


def run(dataset, output_dir, device, deadline):
    started = time.monotonic()
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    if device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but no CUDA device is available")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    data = np.load(dataset, allow_pickle=False)
    report = {"experiment": "post-test-dl-v3", "january_labels_used": False,
              "device": device, "hardware": torch.cuda.get_device_name() if device.startswith("cuda") else platform.processor(),
              "torch_version": torch.__version__, "numpy_version": np.__version__,
              "platform": platform.platform(), "config": CONFIG, "seeds": SEEDS,
              "dataset_sha256": hashlib.sha256(Path(dataset).read_bytes()).hexdigest(),
              "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "status": "running", "turbines": {}}
    try:
        # Complete one model family across turbines before starting the next.
        for family in ("residual_mlp", "feature_transformer"):
            for turbine in TURBINES:
                # Exclude all January targets before any fitting or scoring operation.
                mask = data[turbine + "_valid"] < "2026-01-01T00:00:00Z"
                x, y = data[turbine + "_x"][mask], data[turbine + "_y"][mask]
                valid, issue = data[turbine + "_valid"][mask], data[turbine + "_issue"][mask]
                trials = report["turbines"].setdefault(turbine, {}).setdefault(family, {})
                for cutoff, end in FOLDS:
                    check_deadline(deadline)
                    fit = valid < cutoff
                    test = (issue >= cutoff) & (valid < end)
                    if min(fit.sum(), test.sum()) < 100:
                        raise ValueError("Insufficient outer fold coverage")
                    curve, mean, scale = preprocessing(x[fit], y[fit])
                    tx, ty = tensor_data(x[fit], y[fit], curve, mean, scale, device)
                    vx, _ = tensor_data(x[test], y[test], curve, mean, scale, device)
                    base = curve_predict(curve, x[test, 0])
                    cell = {"status": "running", "cutoff": cutoff, "end_exclusive": end,
                            "train_rows": int(fit.sum()), "validation_rows": int(test.sum()),
                            "unique_train_hours": len(set(valid[fit])), "unique_validation_hours": len(set(valid[test])),
                            "baseline": lead_metrics(y[test], base, x[test]), "seeds": []}
                    trials[cutoff] = cell
                    predictions, train_predictions = [], []
                    for seed in SEEDS:
                        tick = time.monotonic()
                        count, detail = select_epochs(family, seed, x, y, valid, issue, cutoff, device, deadline)
                        model = make_model(family, seed, device)
                        optimizer = optimizer_for(model)
                        for _ in range(count):
                            epoch(model, optimizer, tx, ty, deadline)
                        prediction = base + infer(model, vx)
                        train_prediction = curve_predict(curve, x[fit, 0]) + infer(model, tx)
                        predictions.append(prediction)
                        train_predictions.append(train_prediction)
                        path = output / f"{turbine}-{family}-{cutoff[:10]}-{seed}.pt"
                        torch.save({"state_dict": model.cpu().state_dict(), "family": family,
                                    "mean": mean.tolist(), "scale": scale.tolist(), "curve": curve,
                                    "fit_end_exclusive": cutoff, "seed": seed}, path)
                        detail.update(seed=seed, seconds=time.monotonic() - tick,
                                      parameters=sum(p.numel() for p in model.parameters()),
                                      validation=lead_metrics(y[test], prediction, x[test]),
                                      train=metrics(y[fit], train_prediction),
                                      weight_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                        cell["seeds"].append(detail)
                        write_json(output / "report.json", report)
                        print(json.dumps({"turbine": turbine, "family": family, "cutoff": cutoff,
                                          "seed": seed, "epochs": count,
                                          "rmse": detail["validation"]["all_48"]["rmse"],
                                          "seconds": round(detail["seconds"], 2)}), flush=True)
                    ensemble = np.mean(predictions, axis=0)
                    cell["ensemble"] = lead_metrics(y[test], ensemble, x[test])
                    cell["train_ensemble"] = metrics(y[fit], np.mean(train_predictions, axis=0))
                    cell["seed_rmse_std"] = float(np.std([s["validation"]["all_48"]["rmse"] for s in cell["seeds"]]))
                    path = output / f"{turbine}-{family}-{cutoff[:10]}-predictions.csv"
                    with path.open("w", encoding="utf-8", newline="") as stream:
                        writer = csv.writer(stream)
                        writer.writerow(["issue_time", "valid_time", "actual", "curve", "ensemble", *[f"seed_{s}" for s in SEEDS]])
                        writer.writerows(zip(issue[test], valid[test], y[test], base, ensemble, *predictions))
                    cell["predictions_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                    cell["status"] = "completed"
                    write_json(output / "report.json", report)
        report["status"] = "completed"
    except TimeoutError as error:
        report["status"] = "deadline_reached"
        report["limitation"] = str(error)
    except Exception as error:
        report["status"] = "failed"
        report["error_type"] = type(error).__name__
        raise
    finally:
        report["runtime_seconds"] = time.monotonic() - started
        for turbine, families in report["turbines"].items():
            for family, cells in families.items():
                complete = len(cells) == len(FOLDS) and all(c["status"] == "completed" for c in cells.values())
                if complete:
                    for c in cells.values():
                        c["family_mean_fold_rmse"] = float(np.mean([v["ensemble"]["all_48"]["rmse"] for v in cells.values()]))
        write_json(output / "report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--deadline", required=True, help="Absolute ISO UTC hard stop")
    args = parser.parse_args()
    result = run(args.dataset, args.output_dir, args.device, utc(args.deadline).timestamp())
    print(json.dumps({"status": result["status"], "runtime_seconds": result["runtime_seconds"]}))


if __name__ == "__main__":
    main()
