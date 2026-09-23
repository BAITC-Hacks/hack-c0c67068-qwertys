"""Optional research tests: temporal leakage and actual train/save/load behavior."""
from datetime import datetime, timedelta, timezone
import time

import numpy as np
import pytest

torch = pytest.importorskip("torch")
from src.ml import deep_compare as dl


def test_future_targets_cannot_change_inner_stopping(monkeypatch):
    torch.set_num_threads(2)
    monkeypatch.setitem(dl.CONFIG, "max_epochs", 2)
    rng = np.random.default_rng(7)
    x = rng.normal(size=(1600, 7))
    x[:, 0] = rng.uniform(1, 16, len(x))
    y = x[:, 0] * 0.04 + rng.normal(0, 0.05, len(x))
    start = datetime(2025, 10, 1, tzinfo=timezone.utc)
    valid = np.array([dl.iso(start + timedelta(hours=i)) for i in range(len(x))])
    issue = np.array([dl.iso(start + timedelta(hours=i - 24)) for i in range(len(x))])
    cutoff = "2025-12-01T00:00:00Z"
    before = dl.select_epochs("residual_mlp", 42, x, y, valid, issue, cutoff, "cpu", time.time() + 30)
    y[valid >= cutoff] = 1e6
    after = dl.select_epochs("residual_mlp", 42, x, y, valid, issue, cutoff, "cpu", time.time() + 30)
    assert before == after


@pytest.mark.parametrize("family", ["residual_mlp", "feature_transformer"])
def test_models_train_and_restore_predictions(family, tmp_path):
    torch.set_num_threads(2)
    x = torch.randn(64, 7)
    y = x[:, 0] * 0.1
    model = dl.make_model(family, 42, "cpu")
    before = dl.infer(model, x)
    dl.epoch(model, dl.optimizer_for(model), x, y, time.time() + 30)
    prediction = dl.infer(model, x)
    assert np.isfinite(prediction).all()
    assert not np.array_equal(before, prediction)
    path = tmp_path / "weights.pt"
    torch.save(model.state_dict(), path)
    restored = dl.make_model(family, 137, "cpu")
    restored.load_state_dict(torch.load(path, weights_only=True))
    np.testing.assert_array_equal(prediction, dl.infer(restored, x))
