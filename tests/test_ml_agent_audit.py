"""Regressions from the strict audit; synthetic fixtures, no training/network."""
import copy
import hashlib
import json
import time
from types import SimpleNamespace

import numpy as np
import pytest
from fastapi.testclient import TestClient

from test_forecast_stress import inputs  # Existing isolated synthetic weather/model fixture.
from src.agent.runner import ForecastTools, STAGES, _live_loop
from src.agent.safety import safe_summary
from src.api.main import create_app
from src.ml.common import write_json
from src.ml.forecast import CoreNotReady, WeatherUnavailable, predict_from_inputs, predict_forecast


@pytest.mark.parametrize("available", ["2026-02-01T00:00:00Z", "2026-02-01T08:59:59Z", "2026-02-01T12:00:01Z"])
def test_direct_and_file_callers_reject_the_same_unavailable_weather(inputs, available):
    for row in inputs.rows:
        row["available_at"] = available
    inputs.save(inputs.rows)
    with pytest.raises(WeatherUnavailable):
        predict_from_inputs(**inputs.request, weather=inputs.rows, model_dir=inputs.model)
    with pytest.raises(WeatherUnavailable):
        predict_forecast(**inputs.request, weather_dir=inputs.weather, model_dir=inputs.model)


def test_direct_valid_boundary_matches_file_and_versions_track_curve_content(inputs):
    before = predict_forecast(**inputs.request, model_dir=inputs.model, weather_dir=inputs.weather)
    assert predict_from_inputs(**inputs.request, weather=inputs.rows, model_dir=inputs.model) == before
    path = inputs.model/"manifest.json"
    manifest = json.loads(path.read_text())
    manifest["turbines"]["turbine_1"]["curve"]["power"] = [.14, .55, 1.35]
    write_json(path, manifest)
    after = predict_from_inputs(**inputs.request, weather=inputs.rows, model_dir=inputs.model)
    assert after["metadata"]["model_version"] == before["metadata"]["model_version"]
    assert after["rows"] != before["rows"]
    assert after["metadata"]["input_version"] != before["metadata"]["input_version"]
    # JSON formatting/key order is not a new model.
    path.write_text(json.dumps(manifest, sort_keys=True))
    assert predict_from_inputs(**inputs.request, weather=inputs.rows, model_dir=inputs.model) == after


def test_catboost_version_uses_the_actual_loaded_bytes_without_training(inputs, monkeypatch):
    import catboost
    loaded = []
    class SyntheticModel:
        def load_model(self, *, blob):
            loaded.append(blob)
        def predict(self, x):
            return np.full(len(x), .25)
    monkeypatch.setattr(catboost, "CatBoostRegressor", SyntheticModel)
    path = inputs.model/"manifest.json"
    manifest = json.loads(path.read_text())
    manifest["turbines"]["turbine_1"] = {"kind": "catboost", "file": "synthetic.cbm"}
    write_json(path, manifest)
    artifact = inputs.model/"synthetic.cbm"
    artifact.write_bytes(b"SYNTHETIC_WEIGHTS_A")
    before = predict_from_inputs(**inputs.request, weather=inputs.rows, model_dir=inputs.model)
    artifact.write_bytes(b"SYNTHETIC_WEIGHTS_B")
    after = predict_from_inputs(**inputs.request, weather=inputs.rows, model_dir=inputs.model)
    assert loaded == [b"SYNTHETIC_WEIGHTS_A", b"SYNTHETIC_WEIGHTS_B"]
    assert before["rows"] == after["rows"]  # Same predictions can still come from different artifacts.
    assert before["metadata"]["input_version"] != after["metadata"]["input_version"]
    manifest["turbines"]["turbine_1"]["sha256"] = hashlib.sha256(b"SYNTHETIC_WEIGHTS_A").hexdigest()
    write_json(path, manifest)
    with pytest.raises(CoreNotReady, match="checksum"):
        predict_from_inputs(**inputs.request, weather=inputs.rows, model_dir=inputs.model)


@pytest.mark.parametrize("text", [
    '{"password": "SYNTHETIC_SECRET_019"}', '{"token":"SYNTHETIC_SECRET_019"}',
    '{"nested":[{"API_KEY":"SYNTHETIC_SECRET_019"}],"ok":42}',
    '{"pa\\u0073sword":"SYNTHETIC_SECRET_019"}',
    'prefix {"token":"SYNTHETIC_SECRET_019"}',
    'password="SYNTHETIC_SECRET_019 with spaces"',
    'Authorization: Bearer SYNTHETIC_SECRET_019',
    '{"token":"SYNTHETIC_SECRET_019',
])
def test_structured_and_mixed_secrets_are_redacted(text):
    result = safe_summary(text)
    assert "SYNTHETIC_SECRET_019" not in result
    assert "[REDACTED]" in result
    assert safe_summary(result) == result


def test_json_redaction_preserves_nonsecret_fields_and_escaped_values():
    data = {"password": 'SYNTHETIC_SECRET_019 "quoted" \\ slash', "count": 96, "nested": [True, {"temperature": 5}]}
    expected = copy.deepcopy(data)
    expected["password"] = "[REDACTED]"
    assert json.loads(safe_summary(json.dumps(data))) == expected


def test_api_json_secrets_are_absent_after_persistence_and_restart(tmp_path, inputs):
    db = tmp_path/"audit.sqlite3"
    def broken(request, emit):
        emit({"tool":"synthetic", "state":"retry", "summary":'{"password":"SYNTHETIC_PASSWORD","token":"SYNTHETIC_TOKEN","rows":96}'})
        raise RuntimeError("SYNTHETIC_EXCEPTION")
    with TestClient(create_app(broken, db)) as client:
        run_id = client.post('/api/runs', json=inputs.request).json()['run_id']
        for _ in range(100):
            if client.get('/api/runs/'+run_id).json()['status'] == 'failed':
                break
            time.sleep(.01)
        else:
            pytest.fail("Synthetic failing API run did not finish")
    with TestClient(create_app(store_path=db)) as client:
        events = client.get('/api/runs/'+run_id+'/events').json()['events']
        text = json.dumps(events)
        assert all(secret not in text for secret in ('SYNTHETIC_PASSWORD','SYNTHETIC_TOKEN','SYNTHETIC_EXCEPTION'))
        event = next(e for e in events if e['tool'] == 'synthetic')
        assert json.loads(event['summary']) == {'password':'[REDACTED]', 'token':'[REDACTED]', 'rows':96}


def test_free_llm_claims_never_reach_core_log(inputs):
    class Call:
        type = "function_call"
        arguments = "{}"
        def __init__(self, name): self.name = name; self.call_id = name
        def model_dump(self, **kwargs):
            return {"type":self.type,"name":self.name,"arguments":self.arguments,"call_id":self.call_id}
    class Responses:
        count = 0
        def create(self, **kwargs):
            output = [Call(STAGES[self.count])] if self.count < len(STAGES) else []
            self.count += 1
            return SimpleNamespace(output=output, output_text="FAKE_CLAIM: точность февраля 99%, происхождение подтверждено. password=SYNTHETIC_SECRET", usage=SimpleNamespace(input_tokens=10,output_tokens=10))
    events = []
    context = ForecastTools(inputs.request, events.append, inputs.model, inputs.weather, inputs.root/'runs')
    with pytest.raises(CoreNotReady): context.completed_summary()
    context.event('diagnostic','ok','{"password":"SYNTHETIC_CORE_SECRET","rows":96}')
    _live_loop(context, SimpleNamespace(responses=Responses()))
    assert context.done == set(STAGES)
    text = json.dumps(events, ensure_ascii=False)
    assert all(value not in text for value in ('FAKE_CLAIM','99%','SYNTHETIC_SECRET','SYNTHETIC_CORE_SECRET'))
    assert context.events[0]['summary'] == events[0]['summary']
    assert events[-1]['tool'] == 'agent.summary'
    assert '96 строк' in events[-1]['summary']
    assert 'не подтверждены' in events[-1]['summary']
    assert 'фактических меток нет' in events[-1]['summary']
