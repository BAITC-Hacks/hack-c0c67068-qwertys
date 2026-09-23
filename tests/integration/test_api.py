"""Transport tests use an injected, explicitly synthetic numeric stub (never production fallback)."""
import csv
import io
import time
from datetime import timedelta
from threading import Event

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.api.store import RunStore, now
from src.contracts.schemas import EventInput, ForecastMetadata, ForecastPayload, ForecastRequest, ForecastRow, RunStatus

BODY = {"issue_time": "2026-01-31T23:00:00+06:00", "turbine_ids": ["turbine_1", "turbine_2"], "horizon_hours": 24}


def synthetic_stub(request, emit):
    emit(EventInput(tool="test.stub", state="ok", summary="SYNTHETIC TEST ONLY", stage="forecast"))
    return ForecastPayload(
        rows=[ForecastRow(turbine_id=turbine, issue_time=request.issue_time, valid_time=request.issue_time + timedelta(hours=hour), lead_hours=hour, y_pred=1.2 if hour == 1 else 0.4) for turbine in request.turbine_ids for hour in range(1, request.horizon_hours + 1)],
        metadata=ForecastMetadata(model_version="TEST-STUB", weather_available_at=request.issue_time - timedelta(hours=2), weather_run_time=request.issue_time - timedelta(hours=8), availability_basis="inferred_run_plus_6h", provenance_status="unconfirmed", scada_timezone="UTC+6", timezone_status="inferred"),
        mode="deterministic",
    )


def completed(client, run_id):
    for _ in range(100):
        status = client.get(f"/api/runs/{run_id}").json()
        if status["status"] in ("completed", "failed"):
            return status
        time.sleep(0.01)
    pytest.fail("Local test run did not finish")


def test_without_core_is_not_ready(tmp_path):
    with TestClient(create_app(store_path=tmp_path / 'runs.db')) as client:
        assert client.get('/api/health').json()['forecast_ready'] is False
        result = client.post('/api/runs', json=BODY)
        assert result.status_code == 503
        assert result.json()['error']['code'] == 'not_ready'
        assert client.get('/api/runs').json() == []


@pytest.mark.parametrize('change', [
    {'issue_time': '2026-01-31T23:00:00'}, {'issue_time': 1770000000},
    {'turbine_ids': ['T1']}, {'turbine_ids': ['turbine_1', 'turbine_1']},
    {'horizon_hours': 12}, {'unknown_key': 'sensitive-value'},
])
def test_request_validation(tmp_path, change):
    with TestClient(create_app(store_path=tmp_path / 'runs.db')) as client:
        response = client.post('/api/runs', json={**BODY, **change})
        assert response.status_code == 422
        assert 'sensitive-value' not in response.text


@pytest.mark.parametrize('horizon', [24, 48])
def test_forecast_export_rerun_and_restart(tmp_path, horizon):
    db = tmp_path / 'runs.db'
    with TestClient(create_app(synthetic_stub, db)) as client:
        response = client.post('/api/runs', json={**BODY, 'horizon_hours': horizon})
        assert response.status_code == 202
        run_id = response.json()['run_id']
        status = completed(client, run_id)
        assert status['status'] == 'completed'
        assert status['mode'] == 'deterministic'
        assert len(status['warnings']) >= 2  # uncertainty in provenance and timezone remains visible
        forecast = client.get(f'/api/runs/{run_id}/forecast').json()
        assert len(forecast['rows']) == horizon * 2
        assert forecast['rows'][0]['issue_time'] == '2026-01-31T17:00:00Z'
        assert forecast['rows'][0]['y_pred'] == 1.2  # no unproven clipping
        events = client.get(f'/api/runs/{run_id}/events').json()['events']
        assert [e['seq'] for e in events] == list(range(1, len(events) + 1))
        assert any(e['tool'] == 'test.stub' for e in events)
        export = client.get(f'/api/runs/{run_id}/export.csv')
        csv_rows = list(csv.DictReader(io.StringIO(export.text.lstrip('\ufeff'))))
        assert len(csv_rows) == len(forecast['rows'])
        assert float(csv_rows[0]['y_pred']) == 1.2
        assert csv_rows[0]['unit'] == 'normalized_power'
        second = client.post('/api/runs', json={**BODY, 'horizon_hours': horizon}).json()['run_id']
        assert second != run_id
        assert completed(client, second)['status'] == 'completed'
        assert client.get(f'/api/runs/{run_id}/forecast').json() == forecast
    with TestClient(create_app(store_path=db)) as restarted:
        assert restarted.get(f'/api/runs/{run_id}/forecast').json() == forecast


@pytest.mark.parametrize('fault', ['future_weather', 'duplicate', 'wrong_turbine', 'empty', 'nan', 'bad_lead'])
def test_bad_core_result_cannot_be_success(tmp_path, fault):
    def faulty(request, emit):
        payload = synthetic_stub(request, emit).model_dump()
        if fault == 'future_weather': payload['metadata']['weather_available_at'] = request.issue_time + timedelta(hours=1)
        if fault == 'duplicate': payload['rows'].append(payload['rows'][0])
        if fault == 'wrong_turbine': payload['rows'][0]['turbine_id'] = 'unknown'
        if fault == 'empty': payload['rows'] = []
        if fault == 'nan': payload['rows'][0]['y_pred'] = float('nan')
        if fault == 'bad_lead': payload['rows'][0]['lead_hours'] = 5
        return payload
    with TestClient(create_app(faulty, tmp_path / 'runs.db')) as client:
        run_id = client.post('/api/runs', json=BODY).json()['run_id']
        assert completed(client, run_id)['status'] == 'failed'
        assert client.get(f'/api/runs/{run_id}/forecast').status_code == 409
        assert client.get(f'/api/runs/{run_id}/export.csv').status_code == 409


def test_core_exception_and_event_secrets_are_not_exposed(tmp_path):
    def broken(request, emit):
        emit(EventInput(tool='weather', state='retry', summary='Authorization: Bearer private-value api_key=private-key sk-private123'))
        raise RuntimeError('api_key=private-exception')
    with TestClient(create_app(broken, tmp_path / 'runs.db')) as client:
        run_id = client.post('/api/runs', json=BODY).json()['run_id']
        assert completed(client, run_id)['status'] == 'failed'
        assert 'private' not in client.get(f'/api/runs/{run_id}').text
        assert 'private' not in client.get(f'/api/runs/{run_id}/events').text


def test_queue_bound_and_running_result(tmp_path):
    gate = Event()
    def slow(request, emit):
        gate.wait(timeout=4)
        return synthetic_stub(request, emit)
    with TestClient(create_app(slow, tmp_path / 'runs.db')) as client:
        try:
            ids = [client.post('/api/runs', json=BODY).json()['run_id'] for _ in range(4)]
            assert client.post('/api/runs', json=BODY).status_code == 503
            assert client.get(f'/api/runs/{ids[0]}/forecast').status_code == 409
        finally:
            gate.set()
        assert all(completed(client, id)['status'] == 'completed' for id in ids)


def test_restart_marks_unfinished_failed(tmp_path):
    db = tmp_path / 'runs.db'
    store = RunStore(db)
    request = ForecastRequest.model_validate(BODY)
    store.create(RunStatus(run_id='interrupted', status='running', started_at=now(), updated_at=now(), issue_time=request.issue_time, turbine_ids=request.turbine_ids, horizon_hours=request.horizon_hours))
    with TestClient(create_app(store_path=db)) as client:
        result = client.get('/api/runs/interrupted').json()
        assert result['status'] == 'failed'
        assert result['error']['code'] == 'interrupted'


def test_unknown_run_and_route(tmp_path):
    with TestClient(create_app(store_path=tmp_path / 'runs.db')) as client:
        assert client.get('/api/runs/absent').status_code == 404
        assert client.get('/api/runs/absent/events').status_code == 404
        assert client.get('/api/absent').json()['error']['code'] == 'unknown_endpoint'
