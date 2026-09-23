"""Meaningful temporal, calibration and fail-closed gate checks."""
from datetime import datetime, timedelta, timezone
import time
import numpy as np
import pytest

torch = pytest.importorskip("torch")
from src.ml import quality_cycle as qc


def test_alpha_conservatively_shrinks_and_rejects_corruption():
    residual = np.array([1., -2., 3.])
    assert qc.alpha_fit(residual, residual*.25) == .25
    assert qc.alpha_fit(residual, -residual) == 0
    assert qc.alpha_fit(residual, residual*3) == 1
    assert qc.alpha_fit(residual*0, residual) == 0
    with pytest.raises(ValueError, match="Nonfinite"):
        qc.alpha_fit(residual, np.array([1., np.nan, 3.]))


def test_future_features_and_targets_cannot_change_calibration(monkeypatch):
    torch.set_num_threads(2)
    monkeypatch.setitem(qc.dl.CONFIG, "max_epochs", 2)
    rng = np.random.default_rng(53)
    x = rng.normal(size=(1600, 7))
    x[:, 0] = rng.uniform(1, 16, len(x))
    y = x[:, 0]*.04 + rng.normal(0, .05, len(x))
    start = datetime(2025, 10, 1, tzinfo=timezone.utc)
    valid = np.array([qc.iso(start+timedelta(hours=i)) for i in range(len(x))])
    issue = np.array([qc.iso(start+timedelta(hours=i-24)) for i in range(len(x))])
    cutoff = "2025-12-01T00:00:00Z"
    before = qc.inner_calibration(42, x, y, valid, issue, cutoff, "cpu", time.time()+30)
    x[valid >= cutoff] = 1e6
    y[valid >= cutoff] = -1e6
    after = qc.inner_calibration(42, x, y, valid, issue, cutoff, "cpu", time.time()+30)
    assert before == after


def test_overlapping_origins_cannot_inflate_unique_hours_or_create_ramps():
    valid = np.array(["2025-12-01T01:00:00Z", "2025-12-01T01:00:00Z", "2025-12-01T02:00:00Z"])
    y = np.array([.2, .2, .8])
    p = np.array([.1, .3, .7])
    score = qc.unique_hour_scores(valid, y, {"m": p})["m"]
    assert score["n"] == 2
    assert score["mae"] == pytest.approx(.05)
    ramps = qc.ramps(valid, y)
    assert np.isnan(ramps[:2]).all() and ramps[2] == pytest.approx(.6)
    with pytest.raises(ValueError, match="Conflicting labels"):
        qc.ramps(valid, np.array([.2, .4, .8]))


def test_incomplete_or_positive_uncertainty_cannot_pass_gate():
    assert not qc.gate([], None)["eligible"]
    cells = []
    for cutoff, end in qc.FOLDS:
        scores = {m: {"n": 500, "rmse": .3 if m != "mlp_shrink" else .2, "bias": 0} for m in qc.METHODS}
        cells.append({"status": "completed", "cutoff": cutoff, "seeds": [{"seed": s} for s in qc.dl.SEEDS],
                      "slices": {name: scores for name in ("all", "lead1_24", "lead25_48", "wind_ge8")}})
    assert qc.gate(cells, [-.15, -.05])["eligible"]
    assert not qc.gate(cells, [-.15, .001])["eligible"]
    cells[-1]["slices"].pop("wind_ge8")
    assert not qc.gate(cells, [-.15, -.05])["eligible"]
    cells[-1]["seeds"].pop()
    assert not qc.gate(cells, [-.15, -.05])["eligible"]


def test_prediction_corruption_rejected_before_uncertainty(tmp_path):
    path = tmp_path / "pred.csv"
    path.write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        qc.block_interval([{"prediction_file": path.name, "prediction_sha256": "bad"}], tmp_path)
