"""Independently audit saved test predictions using stdlib, without model code.

Reads local derived SCADA labels; publishes only aggregate findings, never raw data.
"""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path


def utc(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Naive timestamp')
    return result.astimezone(timezone.utc)


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def metrics(rows, column):
    errors = [float(row[column]) - float(row['actual']) for row in rows]
    if not errors or not all(math.isfinite(x) for x in errors):
        raise ValueError('Missing/nonfinite metric inputs')
    return {'n': len(errors), 'mae': sum(map(abs, errors)) / len(errors),
            'rmse': math.sqrt(sum(x*x for x in errors) / len(errors)),
            'bias': sum(errors) / len(errors)}


def audit(report_path, scada_dir, weather_dir):
    report = json.loads(report_path.read_text(encoding='utf-8'))
    start = utc(report['target_split']['validation_end_exclusive'])
    end = utc(report['target_split']['test_end_exclusive'])
    possible = set()
    for path in sorted(weather_dir.glob('????-??-??.jsonl')):
        weather = jsonl(path)
        if not weather:
            continue
        issue = utc(weather[0]['run_time']) + timedelta(hours=12)
        if not start <= issue < end:
            continue
        for row in weather:
            valid = utc(row['valid_time'])
            lead = (valid-issue).total_seconds() / 3600
            if 1 <= lead <= 48 and lead.is_integer() and valid < end:
                if utc(row['available_at']) > issue:
                    raise ValueError('Future weather in test input')
                possible.add((issue, valid))
    findings = {'status': 'PASS', 'unit': report['unit'], 'bias_definition': 'prediction minus actual',
                'report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
                'provenance': 'Conditional on inferred UTC+6 and weather run+9h, not verified historical availability',
                'turbines': {}}
    if report['unit'] != 'normalized_power' or not possible:
        raise ValueError('Unexpected units or empty weather test sample')
    for number in (1, 2):
        turbine = f'turbine_{number}'
        scada_path = scada_dir / f'scada-t{number}-hourly.jsonl'
        if hashlib.sha256(scada_path.read_bytes()).hexdigest() != report['scada_input_sha256'][scada_path.name]:
            raise ValueError(f'{turbine}: SCADA source hash mismatch')
        labels = {utc(row['timestamp']): row['power_normalized'] for row in jsonl(scada_path)
                  if row['coverage'] == 1 and not row['quality_flags']}
        prediction_path = report_path.parent / f'{turbine}-test-predictions.csv'
        expected = report['turbines'][turbine]
        prediction_hash = hashlib.sha256(prediction_path.read_bytes()).hexdigest()
        if prediction_hash != expected['test_predictions_sha256']:
            raise ValueError(f'{turbine}: prediction checksum mismatch')
        with prediction_path.open(encoding='utf-8-sig', newline='') as stream:
            rows = list(csv.DictReader(stream))
        pairs = set()
        for row in rows:
            issue, valid = utc(row['issue_time']), utc(row['valid_time'])
            key = (issue, valid)
            if row['turbine_id'] != turbine or key in pairs or key not in possible:
                raise ValueError(f'{turbine}: unexpected or duplicate prediction identity')
            pairs.add(key)
            if not start <= issue < valid < end or (valid-issue).total_seconds() != int(row['lead_hours'])*3600:
                raise ValueError(f'{turbine}: invalid test time boundary')
            if valid not in labels or not math.isclose(float(row['actual']), labels[valid], abs_tol=1e-12, rel_tol=1e-12):
                raise ValueError(f'{turbine}: actual label differs from independently loaded SCADA')
        available = {(issue, valid) for issue, valid in possible if valid in labels}
        if pairs != available:
            raise ValueError(f'{turbine}: silently omitted or extra labelled pairs')
        slices = {'all_48': rows, 'hours_1_24': [r for r in rows if int(r['lead_hours']) <= 24],
                  'hours_25_48': [r for r in rows if int(r['lead_hours']) > 24]}
        result = {model: {name: metrics(group, model) for name, group in slices.items()}
                  for model in ('nwp_curve', 'catboost')}
        for model, groups in result.items():
            for group, values in groups.items():
                for key, value in values.items():
                    if not math.isclose(value, expected['test'][model][group][key], rel_tol=1e-10, abs_tol=1e-12):
                        raise ValueError(f'{turbine}/{model}/{group}/{key}: reported metric mismatch')
        coverage = len(pairs) / len(possible)
        if expected['test_coverage']['possible_pairs'] != len(possible) or not math.isclose(coverage, expected['test_coverage']['coverage']):
            raise ValueError(f'{turbine}: coverage denominator mismatch')
        delta = result['catboost']['all_48']['rmse'] - result['nwp_curve']['all_48']['rmse']
        if not math.isclose(delta, expected['candidate_rmse_delta'], abs_tol=1e-12):
            raise ValueError(f'{turbine}: baseline comparison mismatch')
        findings['turbines'][turbine] = {'prediction_sha256': prediction_hash, 'metrics': result,
            'candidate_rmse_delta': delta, 'labelled_pairs': len(pairs), 'possible_pairs': len(possible),
            'coverage': coverage, 'unique_target_hours': len({v for _, v in pairs}),
            'overlapping_origins_preserved': len(pairs) > len({v for _, v in pairs})}
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--scada-dir', type=Path, required=True)
    parser.add_argument('--weather-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    findings = audit(args.report, args.scada_dir, args.weather_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(findings, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(findings, ensure_ascii=True))


if __name__ == '__main__':
    main()
