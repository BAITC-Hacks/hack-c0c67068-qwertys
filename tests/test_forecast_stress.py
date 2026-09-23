"""Synthetic robustness and metamorphic checks, never accuracy benchmarks."""
import copy
import json
from datetime import timedelta
from types import SimpleNamespace

import numpy as np
import pytest

from src.ml.common import iso, utc, write_json
from src.ml.forecast import predict_forecast, WeatherUnavailable, InvalidForecastRequest
from src.agent.runner import ForecastTools, run_forecast, STAGES


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    monkeypatch.setenv("WEATHER_FETCH_POLICY", "never")
    monkeypatch.setenv("OPENAI_BUDGET_LEDGER", str(tmp_path/"budget.json"))
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini-2025-04-14")
    monkeypatch.setenv("OPENAI_SESSION_BUDGET_USD", "1")
    model, weather = tmp_path/"model", tmp_path/"weather"
    weather.mkdir()
    spec = {"kind": "curve", "curve": {"wind": [1, 8, 16], "power": [-.01, .4, 1.2]}}
    write_json(model/"manifest.json", {"training_end_exclusive": "2026-01-31T00:00:00Z",
               "model_version": "SYNTHETIC-STRESS", "scada_timezone": "UTC+6 hypothesis",
               "turbines": {"turbine_1": spec, "turbine_2": spec}})
    issue = "2026-02-01T12:00:00Z"
    rows = [{"provider": "SYNTHETIC", "model": "SYNTHETIC", "run_time": "2026-02-01T00:00:00Z",
             "available_at": "2026-02-01T09:00:00Z", "availability_basis": "inferred_run_plus_9h",
             "provenance_status": "unconfirmed", "valid_time": iso(utc(issue)+timedelta(hours=i)),
             "source_reference": "synthetic", "variables": {"wind_speed_100m_m_s": i/3,
                "wind_direction_100m_deg": i*7 % 360, "temperature_2m_c": -10+i/2}}
            for i in range(1, 49)]
    def save(values):
        (weather/"2026-02-01.jsonl").write_text("\n".join(json.dumps(r) for r in values), encoding="utf-8")
    save(rows)
    request = {"issue_time": issue, "turbine_ids": ["turbine_1", "turbine_2"], "horizon_hours": 48}
    return SimpleNamespace(model=model, weather=weather, root=tmp_path, rows=rows, request=request, save=save)


def predict(d, **changes):
    return predict_forecast(**{**d.request, **changes}, model_dir=d.model, weather_dir=d.weather)


@pytest.mark.parametrize("variable", ["wind_speed_100m_m_s", "wind_direction_100m_deg", "temperature_2m_c"])
@pytest.mark.parametrize("bad", [None, True, "12", float("nan"), float("inf"), -float("inf")])
def test_bad_weather_never_becomes_success(inputs, variable, bad):
    inputs.rows[19]["variables"][variable] = bad
    inputs.save(inputs.rows)
    with pytest.raises(WeatherUnavailable):
        predict(inputs)


@pytest.mark.parametrize("fault", ["duplicate", "mixed_source", "wrong_cycle", "early_publication", "late_publication", "missing_middle"])
def test_temporal_or_provenance_damage_fails_entire_horizon(inputs, fault):
    rows = inputs.rows
    if fault == "duplicate": rows.append(copy.deepcopy(rows[20]))
    if fault == "mixed_source": rows[20]["source_reference"] = "different"
    if fault == "wrong_cycle": rows[20]["run_time"] = "2026-01-31T00:00:00Z"
    if fault == "early_publication": rows[20]["available_at"] = "2026-02-01T08:59:59Z"
    if fault == "late_publication": rows[20]["available_at"] = "2026-02-01T12:00:01Z"
    if fault == "missing_middle": rows.pop(20)
    inputs.save(rows)
    with pytest.raises(WeatherUnavailable): predict(inputs)


def test_offsets_order_and_horizon_prefix_do_not_change_predictions(inputs):
    full = predict(inputs)
    inputs.save(list(reversed(inputs.rows)))
    short = predict(inputs, issue_time="2026-02-01T18:00:00+06:00", horizon_hours=24,
                    turbine_ids=["turbine_2", "turbine_1"])
    mapping = {(r["turbine_id"],r["valid_time"]): r for r in full["rows"]}
    assert len(short["rows"]) == 48
    assert all(r == mapping[r["turbine_id"],r["valid_time"]] for r in short["rows"])
    assert predict(inputs)["rows"] == full["rows"]


def test_extreme_supported_values_are_finite_and_extrapolation_visible(inputs):
    for i, row in enumerate(inputs.rows):
        row["variables"]["wind_speed_100m_m_s"] = 0 if i%2 else 60
        row["variables"]["temperature_2m_c"] = -60 if i%2 else 50
    inputs.save(inputs.rows)
    result = predict(inputs)
    assert all(np.isfinite(r["y_pred"]) for r in result["rows"])
    assert {r["y_pred"] for r in result["rows"]} == {-.01, 1.2}
    assert any("за диапазоном" in w for w in result["warnings"])


def test_tool_order_idempotency_and_pinned_input_version(inputs):
    events = []
    request = {**inputs.request, "input_version": "wrong-version"}
    context = ForecastTools(request, events.append, inputs.model, inputs.weather, inputs.root/"runs")
    assert context.call("export")["error"] == "prerequisite_missing"
    assert not events
    context.call("weather")
    before = list(events)
    assert context.call("weather")["status"] == "already_completed"
    assert events == before
    context.call("prepare")
    with pytest.raises(InvalidForecastRequest, match="input_version"):
        context.call("forecast")
    assert not list((inputs.root/"runs").glob("*/forecast.csv"))


@pytest.mark.parametrize("behavior", ["premature_final", "wrong_order", "repeated_weather", "unexpected_args"])
def test_bad_llm_behavior_is_bounded_and_cannot_publish_success(inputs, behavior):
    class Call:
        type = "function_call"
        call_id = "synthetic"
        def __init__(self, name, arguments="{}"):
            self.name, self.arguments = name, arguments
        def model_dump(self, **kwargs):
            return {"type": self.type, "name": self.name, "call_id": self.call_id, "arguments": self.arguments}
    class Responses:
        calls = 0
        def create(self, **kwargs):
            self.calls += 1
            output = [] if behavior == "premature_final" else [Call(
                "export" if behavior == "wrong_order" else "weather",
                '{"override":true}' if behavior == "unexpected_args" else "{}")]
            return SimpleNamespace(output=output, output_text="synthetic", usage=SimpleNamespace(input_tokens=10, output_tokens=5))
    responses = Responses()
    with pytest.raises((RuntimeError, ValueError)):
        run_forecast(inputs.request, lambda e:None, model_dir=inputs.model, weather_dir=inputs.weather,
                     output_dir=inputs.root/"runs", agent_mode="live", client=SimpleNamespace(responses=responses))
    assert responses.calls <= 12
    assert not list((inputs.root/"runs").glob("*/forecast.csv"))
    statuses = list((inputs.root/"runs").glob("*/status.json"))
    assert len(statuses) == 1 and json.loads(statuses[0].read_text())["status"] == "failed"
