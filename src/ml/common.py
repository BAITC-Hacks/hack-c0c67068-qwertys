"""Shared time, features and baseline; no February observations required."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

TURBINES = ("turbine_1", "turbine_2")
FEATURES = ["wind100", "temperature2", "direction_sin", "direction_cos", "hour_sin", "hour_cos", "lead_hours"]


def utc(value):
    value = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value
    if value.tzinfo is None:
        raise ValueError("Time must include an explicit UTC offset")
    return value.astimezone(timezone.utc)


def iso(value):
    return utc(value).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_jsonl(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def features(rows, issue_time):
    issue = utc(issue_time)
    output = []
    for row in rows:
        v = row["variables"]
        valid = utc(row["valid_time"])
        direction = np.deg2rad(v["wind_direction_100m_deg"])
        hour = valid.hour * 2 * np.pi / 24
        output.append([v["wind_speed_100m_m_s"], v["temperature_2m_c"], np.sin(direction), np.cos(direction), np.sin(hour), np.cos(hour), (valid-issue).total_seconds()/3600])
    result = np.asarray(output, dtype=float)
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite feature")
    return result


def fit_curve(wind, target):
    """Fixed 1 m/s bins, means interpolated across empty bins; no arbitrary cap."""
    wind, target = np.asarray(wind), np.asarray(target)
    buckets = np.floor(wind).astype(int)
    centers, means = [], []
    for key in sorted(set(buckets)):
        mask = buckets == key
        if mask.sum() >= 5:
            centers.append(float(wind[mask].mean()))
            means.append(float(target[mask].mean()))
    if len(centers) < 2:
        raise ValueError("Insufficient wind support to fit baseline")
    return {"wind": centers, "power": means, "kind": "binned_mean_1ms"}


def curve_predict(curve, wind):
    return np.interp(wind, curve["wind"], curve["power"])


def metrics(actual, predicted):
    residual = np.asarray(actual) - np.asarray(predicted)
    return {"n": len(residual), "mae": float(np.abs(residual).mean()), "rmse": float(np.sqrt(np.mean(residual**2))), "bias": float(-residual.mean())}
