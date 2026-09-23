from __future__ import annotations
import csv, hashlib, importlib.metadata, importlib.util, json, math, os, platform, sys, zipfile
from pathlib import Path
from datetime import datetime, timezone

root = Path.cwd().resolve()
archive = Path(sys.argv[1])
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
assert not (root/'.git').exists()
assert not (root/'.env').exists()
assert not os.getenv('OPENAI_API_KEY')
assert os.getenv('PYTHON_DOTENV_DISABLED') == '1'
assert Path(sys.prefix).resolve() == root/'.venv'
assert 'include-system-site-packages = false' in (root/'.venv/pyvenv.cfg').read_text(encoding='utf-8')
assert not any('worktrees' in p.lower() for p in sys.path)
with zipfile.ZipFile(archive) as z:
    files = [n for n in z.namelist() if not n.endswith('/')]
    for name in files:
        assert (root/name).read_bytes() == z.read(name), name
versions = {}
for line in (root/'requirements-lock.txt').read_text().splitlines():
    if not line or line.startswith('#'): continue
    name, version = line.split('==')
    assert importlib.metadata.version(name) == version, name
    versions[name] = version
import src.agent.runner, src.ml.forecast, src.weather.open_meteo
for module in (src.agent.runner, src.ml.forecast, src.weather.open_meteo):
    assert Path(module.__file__).resolve().is_relative_to(root/'src')
model = root/'models/production/manifest.json'
assert model.read_bytes() == (root/'coordination/research/C2/model-manifest-v1.json').read_bytes()
manifest = read(model)
assert manifest['model_version'] == 'nwp-tabular-7f1b4f31e9bb'
assert all(spec['kind'] == 'curve' for spec in manifest['turbines'].values())
weather = read(root/'artifacts/c1/weather-batch-manifest.json')
assert list(weather['runs']) == ['2026-01-31']
entry = weather['runs']['2026-01-31']
assert entry['status'] == 'ready' and entry['selected_hours'] == 48
assert sha(root/entry['cache_file']) == entry['source_sha256']
assert not Path(entry['cache_file']).is_absolute() and not Path(entry['rows_file']).is_absolute()
outputs = []
forecast_by_rows = {}
for folder in sorted((root/'artifacts/clean-runs').iterdir()):
    payload = read(folder/'forecast.json')
    usage = read(folder/'usage.json')
    rows = payload['rows']
    assert read(folder/'status.json')['status'] == 'completed'
    assert payload['mode'] == 'deterministic'
    assert usage['input_tokens'] == usage['output_tokens'] == usage['estimated_usd'] == 0
    assert not usage.get('requests')
    assert len(rows) in (48,96)
    assert len({(r['turbine_id'],r['valid_time']) for r in rows}) == len(rows)
    assert all(math.isfinite(r['y_pred']) for r in rows)
    with (folder/'forecast.csv').open(encoding='utf-8-sig',newline='') as stream:
        saved = list(csv.DictReader(stream))
    assert len(saved) == len(rows)
    for a,b in zip(rows,saved):
        assert all(a[k] == b[k] for k in ('turbine_id','issue_time','valid_time'))
        assert a['y_pred'] == float(b['y_pred']) and a['lead_hours'] == int(b['lead_hours'])
    events = read(folder/'events.json')
    assert [e['tool'] for e in events if e['state']=='ok'] == ['weather','prepare','forecast','validate','export']
    forecast_by_rows[len(rows)] = {(r['turbine_id'],r['valid_time']):r['y_pred'] for r in rows}
    outputs.append({'run_id':folder.name,'rows':len(rows),'csv_sha256':sha(folder/'forecast.csv'),'elapsed_seconds':usage['elapsed_seconds'],'csv_json_equal':True,'llm_requests':0})
assert len(outputs) == 2 and set(forecast_by_rows) == {48,96}
assert all(forecast_by_rows[96][key] == value for key,value in forecast_by_rows[48].items())
api = read(root/'api-smoke.json')
assert api['status'] == 'PASS' and [r['rows'] for r in api['runs']] == [96,48,96]
api_usage = [read(p) for p in (root/'artifacts/api-runs').glob('*/usage.json')]
assert len(api_usage) == 3
assert all(u['input_tokens']==u['output_tokens']==u['estimated_usd']==0 and not u.get('requests') for u in api_usage)
result = {
 'status':'PASS','source_commit':'1895090','verified_at_utc':datetime.now(timezone.utc).isoformat(),
 'archive_sha256':sha(archive),'archive_files_unchanged':len(files),
 'python':platform.python_version(),'isolated_new_venv':True,'locked_packages_verified':len(versions),
 'system_site_packages':False,'torch_installed':importlib.util.find_spec('torch') is not None,
 'env_file_present':False,'credentials_used':False,'existing_worktree_runtime_paths':False,
 'model_version':manifest['model_version'],'tracked_manifest_sha256':sha(model),'model_refitted':False,
 'weather':{'fresh_provider_download':True,'run_date':'2026-01-31','selected_hours':48,'raw_sha256':entry['source_sha256'],'response_bytes':entry['response_bytes'],'provenance_status':entry['provenance_status']},
 'cli_runs':outputs,'horizon_prefix_equal':True,'api_smoke':api,
 'total_llm_requests':0,'estimated_paid_api_usd':0,
 'scope':'Clean core install, provider fetch, CLI and HTTP. No frontend build, training or accuracy reevaluation.',
 'limitations':['Historical weather publication and SCADA UTC+6 remain inferred','No February observed labels','Wheel cache was reused by pip; installed packages were not copied from another environment']
}
(root/'clean-core-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
