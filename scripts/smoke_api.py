"""Verify a configured real local API; creates three retained runs, no fixtures."""
import argparse
import csv
import io
import json
import time
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--issue-time', default='2026-01-31T12:00:00Z')
    args = parser.parse_args()

    def request(path, body=None, raw=False):
        data = json.dumps(body).encode() if body is not None else None
        with urlopen(Request(args.base_url+path, data=data, headers={'Content-Type': 'application/json'}), timeout=15) as response:
            content = response.read().decode('utf-8-sig')
        return content if raw else json.loads(content)

    assert request('/api/health')['forecast_ready'], 'Real core is not ready'
    results = []
    first = None
    for horizon in (48, 24, 48):
        started = time.perf_counter()
        status = request('/api/runs', {'issue_time': args.issue_time, 'turbine_ids': ['turbine_1', 'turbine_2'], 'horizon_hours': horizon})
        run_id = status['run_id']
        deadline = time.monotonic()+240
        while status['status'] not in ('completed', 'failed') and time.monotonic() < deadline:
            time.sleep(0.05)
            status = request(f'/api/runs/{run_id}')
        assert status['status'] == 'completed', status
        duration = time.perf_counter()-started
        forecast = request(f'/api/runs/{run_id}/forecast')
        rows = forecast['rows']
        exported = list(csv.DictReader(io.StringIO(request(f'/api/runs/{run_id}/export.csv', raw=True))))
        assert len(rows) == len(exported) == horizon*2
        for row, saved in zip(rows, exported):
            assert saved['unit'] == forecast['unit'] == 'normalized_power'
            for key in ('turbine_id', 'issue_time', 'valid_time'):
                assert row[key] == saved[key]
            assert float(saved['y_pred']) == row['y_pred']
            assert int(saved['lead_hours']) == row['lead_hours']
        events = request(f'/api/runs/{run_id}/events')['events']
        tools = [event['tool'] for event in events if event['state'] == 'ok']
        assert all(name in tools for name in ('weather', 'prepare', 'forecast', 'validate', 'export'))
        if status['mode'] == 'deterministic':
            assert 'llm' not in tools
        assert status['warnings'] and forecast['metadata']['model_version']
        results.append({'run_id': run_id, 'horizon': horizon, 'rows': len(rows), 'mode': status['mode'], 'duration_seconds': round(duration, 4), 'tools': tools})
        if first is None:
            first = forecast
    assert len({r['run_id'] for r in results}) == 3
    assert request(f"/api/runs/{first['run_id']}/forecast") == first
    print(json.dumps({'status': 'PASS', 'runs': results, 'model_version': first['metadata']['model_version'], 'limitations': 'Historical weather availability and SCADA timezone remain inferred; deterministic is not LLM execution.'}))


if __name__ == '__main__':
    main()
