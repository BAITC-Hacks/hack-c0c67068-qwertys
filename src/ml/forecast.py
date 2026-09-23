"""Callable numerical forecast, accepting only weather available by issue time."""
from __future__ import annotations
import json
import hashlib
import os
from datetime import timedelta
from pathlib import Path
import numpy as np
from src.ml.common import TURBINES, curve_predict, features, fingerprint, iso, read_jsonl, utc
from src.weather.open_meteo import select_horizon, probe


class CoreNotReady(RuntimeError):
    pass


class WeatherUnavailable(RuntimeError):
    pass


class InvalidForecastRequest(ValueError):
    pass


def validate_request(issue_time, turbine_ids, horizon_hours):
    issue = utc(issue_time)
    if issue.minute or issue.second or issue.microsecond:
        raise InvalidForecastRequest("issue_time must be an exact hour")
    if horizon_hours not in (24, 48) or not turbine_ids or len(set(turbine_ids)) != len(turbine_ids) or not set(turbine_ids) <= set(TURBINES):
        raise InvalidForecastRequest("Expected unique turbine_1/turbine_2 and horizon 24/48")
    return issue


def load_weather(issue_time, horizon_hours, weather_dir=None, *, fetch_policy=None):
    issue = utc(issue_time)
    directory = Path(weather_dir or os.getenv("WEATHER_RUNS_DIR", "data/cache/weather_runs"))
    # Daily 00Z run: newest cycle passing the documented +9h assumption.
    run = (issue - timedelta(hours=9)).replace(hour=0, minute=0, second=0, microsecond=0)
    path = directory / (run.strftime("%Y-%m-%d") + ".jsonl")
    policy=fetch_policy or os.getenv("WEATHER_FETCH_POLICY","never")
    if policy not in ("never","missing","refresh"): raise InvalidForecastRequest("Unknown WEATHER_FETCH_POLICY")
    if policy=="refresh" or (policy=="missing" and not path.is_file()):
        try:
            rows,report,_=probe(43.645150,78.535604,iso(run),directory/"raw",forecast_hours=72)
            select_horizon(rows,iso(issue),horizon_hours)
            directory.mkdir(parents=True,exist_ok=True)
            temporary=path.with_suffix(".jsonl.partial")
            temporary.write_text("\n".join(json.dumps(row,ensure_ascii=False) for row in rows)+"\n",encoding="utf-8")
            temporary.replace(path)
        except Exception as error:
            raise WeatherUnavailable("External weather retrieval or validation failed") from error
    if not path.is_file():
        raise WeatherUnavailable("Required weather cycle is absent from WEATHER_RUNS_DIR")
    rows = read_jsonl(path)
    if not rows or any(utc(row["run_time"]) != run for row in rows):
        raise WeatherUnavailable("Weather file contains the wrong initialization cycle")
    if len({row["valid_time"] for row in rows}) != len(rows):
        raise WeatherUnavailable("Duplicate weather valid_time")
    if len({row["source_reference"] for row in rows}) != 1:
        raise WeatherUnavailable("Mixed source references in weather cycle")
    try:
        selected = select_horizon(rows, iso(issue), horizon_hours)
    except (KeyError, ValueError) as error:
        raise WeatherUnavailable("Weather cycle lacks a valid available complete horizon") from error
    for row in selected:
        if utc(row["available_at"]) < run + timedelta(hours=9):
            raise WeatherUnavailable("Weather metadata violates the +9h availability gate")
    return selected


def load_model(model_dir=None):
    directory = Path(model_dir or os.getenv("MODEL_DIR", "models/production"))
    path = directory / "manifest.json"
    if not path.is_file():
        raise CoreNotReady("Model manifest is absent; run src.ml.train first")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    utc(manifest["training_end_exclusive"])
    if not manifest.get("model_version") or set(manifest["turbines"])!=set(TURBINES):
        raise CoreNotReady("Model manifest identity is invalid")
    for spec in manifest["turbines"].values():
        if spec["kind"] == "catboost":
            artifact=directory/spec["file"]
            if not artifact.is_file(): raise CoreNotReady("Trained model artifact is absent")
            if spec.get("sha256") and hashlib.sha256(artifact.read_bytes()).hexdigest()!=spec["sha256"]:
                raise CoreNotReady("Trained model artifact checksum mismatch")
        elif spec["kind"]=="curve":
            wind=np.asarray(spec["curve"]["wind"],dtype=float); power=np.asarray(spec["curve"]["power"],dtype=float)
            if wind.ndim!=1 or power.shape!=wind.shape or len(wind)<2 or not np.isfinite(wind).all() or not np.isfinite(power).all() or not (np.diff(wind)>0).all():
                raise CoreNotReady("Model calibration curve is malformed")
        else:
            raise CoreNotReady("Unsupported model kind")
    return directory, manifest


def predict_from_inputs(issue_time, turbine_ids, horizon_hours, weather, model_dir=None):
    issue = validate_request(issue_time, turbine_ids, horizon_hours)
    directory, manifest = load_model(model_dir)
    if utc(manifest["training_end_exclusive"]) > issue:
        raise InvalidForecastRequest("Model training cutoff is after requested issue time")
    weather = select_horizon(weather, iso(issue), horizon_hours)
    x = features(weather, issue)
    output = []
    model_warnings=[]
    for turbine in turbine_ids:
        spec = manifest["turbines"][turbine]
        if spec["kind"] == "catboost":
            from catboost import CatBoostRegressor
            model = CatBoostRegressor()
            model.load_model(str(directory / spec["file"]))
            prediction = model.predict(x*np.array(spec.get("feature_mask",[1]*7)))
        elif spec["kind"] == "curve":
            prediction = curve_predict(spec["curve"], x[:, 0])
            outside=(x[:,0]<spec["curve"]["wind"][0])|(x[:,0]>spec["curve"]["wind"][-1])
            if outside.any(): model_warnings.append(f"{turbine}: {int(outside.sum())} часов за диапазоном обученной кривой ветра; использовано ближайшее крайнее значение кривой.")
        else:
            raise CoreNotReady("Unsupported model kind")
        if not np.isfinite(prediction).all():
            raise CoreNotReady("Model produced nonfinite predictions")
        for lead, (row, value) in enumerate(zip(weather, prediction), start=1):
            output.append({"turbine_id": turbine, "issue_time": iso(issue), "valid_time": row["valid_time"], "lead_hours": lead, "y_pred": float(value)})
    first = weather[0]
    input_version = fingerprint({"model": manifest["model_version"], "weather": weather})
    return {"rows": output, "mode": "deterministic", "metadata": {"model_version": manifest["model_version"], "input_version": input_version, "weather_provider": first["provider"], "weather_model": first["model"], "weather_run_time": first["run_time"], "weather_available_at": first["available_at"], "availability_basis": first["availability_basis"], "scada_timezone": manifest["scada_timezone"], "timezone_status": "inferred", "provenance_status": first["provenance_status"]}, "warnings": ["Архивная погода Open-Meteo; публикация на момент выпуска не подтверждена (+9h — допущение).", "Часовой пояс SCADA принят как фиксированный UTC+6; подтверждения владельца нет.", "Мощность в исходных нормализованных единицах; это не МВт и не энергия.", "Февральских фактических меток нет; февральские метрики не вычислялись.",*model_warnings]}


def predict_forecast(issue_time: str, turbine_ids: list[str], horizon_hours: int = 48, *, model_dir=None, weather_dir=None) -> dict:
    validate_request(issue_time, turbine_ids, horizon_hours)
    weather = load_weather(issue_time, horizon_hours, weather_dir)
    return predict_from_inputs(issue_time, turbine_ids, horizon_hours, weather, model_dir)
