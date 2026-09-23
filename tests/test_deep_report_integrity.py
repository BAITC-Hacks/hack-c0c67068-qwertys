"""Gate regression: a completed report must never hide corrupt DL evidence."""
import copy
import csv
import hashlib

import pytest

from src.ml.deep_report import verify_cell


def evidence(tmp_path):
    stem = "turbine_1-residual_mlp-2025-12-01"
    path = tmp_path / f"{stem}-predictions.csv"
    seeds = [42, 137, 2026]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["issue_time", "valid_time", "actual", "curve", "ensemble", *[f"seed_{s}" for s in seeds]])
        writer.writerow(["2025-12-01T12:00:00Z", "2025-12-01T13:00:00Z", 0, 1, 2, 1, 2, 3])
    records = []
    for seed in seeds:
        weight = tmp_path / f"{stem}-{seed}.pt"
        weight.write_bytes(f"trusted fixture {seed}".encode())
        records.append({"seed": seed, "weight_sha256": hashlib.sha256(weight.read_bytes()).hexdigest()})
    cell = {"seeds": records, "predictions_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "validation_rows": 1,
            "baseline": {"all_48": {"n": 1, "rmse": 1, "mae": 1, "bias": 1}},
            "ensemble": {"all_48": {"n": 1, "rmse": 2, "mae": 2, "bias": 2}}}
    return path, cell, seeds


def check(tmp_path, cell, seeds):
    return verify_cell(tmp_path, "turbine_1", "residual_mlp", "2025-12-01T00:00:00Z", cell, seeds)


def test_completed_gate_rejects_tampered_prediction_and_weights(tmp_path):
    path, cell, seeds = evidence(tmp_path)
    assert check(tmp_path, cell, seeds) == path
    original = path.read_bytes()
    path.write_bytes(original + b"\n")
    with pytest.raises(ValueError, match="prediction evidence SHA"):
        check(tmp_path, cell, seeds)
    path.write_bytes(original)
    next(tmp_path.glob("*.pt")).write_bytes(b"replaced weights")
    with pytest.raises(ValueError, match="checkpoint evidence SHA"):
        check(tmp_path, cell, seeds)


def test_completed_gate_rejects_missing_seed_and_stale_metrics(tmp_path):
    _, cell, seeds = evidence(tmp_path)
    incomplete = copy.deepcopy(cell)
    incomplete["seeds"].pop()
    with pytest.raises(ValueError, match="three frozen seeds"):
        check(tmp_path, incomplete, seeds)
    cell["ensemble"]["all_48"]["rmse"] = 0.01
    with pytest.raises(ValueError, match="reported metrics"):
        check(tmp_path, cell, seeds)
