"""Pretest-only UTC-offset diagnostic against the same archived NWP rows.

This is an alignment diagnostic, not proof of SCADA timezone or model skill.
Only November–December SCADA rows are eligible; January labels are excluded
even near the UTC year boundary.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from .scada import prepare_hourly

START_UTC = datetime(2025, 11, 1, tzinfo=timezone.utc)
# At fixed UTC+7, this is local 2026-01-01 00:00. Earlier UTC hours
# therefore use no January-local source rows under any tested offset.
END_UTC = datetime(2025, 12, 31, 17, tzinfo=timezone.utc)
SHIFTS = (5, 6, 7)


def _source_path(cases_dir: Path, turbine_id: str) -> Path:
    suffix = "turbine 1.csv" if turbine_id == "turbine_1" else "turbine 2.csv"
    matches = list(cases_dir.glob("*" + suffix))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one official CSV ending with {suffix}: {matches}")
    return matches[0]


def _scores(points: list[tuple[float, float]]) -> dict:
    count = len(points)
    if count < 3:
        return {"n": count, "pearson_r": None, "mae_m_s": None, "bias_nwp_minus_scada_m_s": None}
    mx = sum(x for x, _ in points) / count
    my = sum(y for _, y in points) / count
    covariance = sum((x - mx) * (y - my) for x, y in points)
    vx = sum((x - mx) ** 2 for x, _ in points)
    vy = sum((y - my) ** 2 for _, y in points)
    return {
        "n": count,
        "pearson_r": covariance / math.sqrt(vx * vy) if vx > 0 and vy > 0 else None,
        "mae_m_s": sum(abs(x - y) for x, y in points) / count,
        "bias_nwp_minus_scada_m_s": sum(x - y for x, y in points) / count,
    }


def analyse(cases_dir: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("provenance_status") != "unconfirmed":
        raise ValueError("Unexpected weather provenance status")
    weather = []
    for run_day, entry in sorted(manifest["runs"].items()):
        if not "2025-11-01" <= run_day <= "2025-12-31":
            continue
        if entry.get("status") != "ready" or entry.get("selected_hours") != 48:
            raise ValueError(f"Weather run incomplete: {run_day}")
        issue = datetime.fromisoformat(entry["issue_time"].replace("Z", "+00:00"))
        for line in Path(entry["rows_file"]).read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            valid = datetime.fromisoformat(row["valid_time"].replace("Z", "+00:00"))
            if not START_UTC <= valid < END_UTC:
                continue
            lead = int((valid - issue).total_seconds() / 3600)
            weather.append((entry["issue_time"], row["valid_time"], lead, row["variables"]["wind_speed_100m_m_s"]))
    if not weather:
        raise ValueError("No pretest weather rows")
    maps = {}
    source_sha = {}
    candidate_complete_hours = {}
    for turbine_id in ("turbine_1", "turbine_2"):
        path = _source_path(cases_dir, turbine_id)
        for offset in SHIFTS:
            observations, report = prepare_hourly(
                path, turbine_id, utc_offset_hours=offset,
                start_utc=START_UTC, end_utc=END_UTC,
            )
            complete = {
                row["timestamp"]: row["wind_m_s"]
                for row in observations
                if row["coverage"] == 1 and not row["quality_flags"]
            }
            maps[(turbine_id, offset)] = complete
            candidate_complete_hours[f"{turbine_id}_UTC+{offset}"] = len(complete)
            source_sha[turbine_id] = report["source_sha256"]
    common_hours = set.intersection(*(set(value) for value in maps.values()))
    common_hours &= {valid for _, valid, _, _ in weather}
    common_pairs = [item for item in weather if item[1] in common_hours]
    if not common_pairs:
        raise ValueError("No common fully observed target hours")
    metrics = {}
    for turbine_id in ("turbine_1", "turbine_2"):
        metrics[turbine_id] = {}
        for offset in SHIFTS:
            observed = maps[(turbine_id, offset)]
            metrics[turbine_id][f"UTC+{offset}"] = {}
            for name, low, high in (("all", 1, 48), ("lead_1_24", 1, 24), ("lead_25_48", 25, 48)):
                points = [(nwp_wind, observed[valid]) for _, valid, lead, nwp_wind in common_pairs if low <= lead <= high]
                metrics[turbine_id][f"UTC+{offset}"][name] = _scores(points)
    return {
        "purpose": "pretest wind alignment diagnostic, not timezone proof",
        "scada_local_months_allowed": "2025-11 and 2025-12 only",
        "utc_start_inclusive": START_UTC.isoformat(),
        "utc_end_exclusive": END_UTC.isoformat(),
        "weather_run_range": ["2025-11-01", "2025-12-31"],
        "weather_issue_rule": "00Z run, 12Z issue, 48h forecast; only valid times before end cutoff",
        "weather_availability_basis": manifest["availability_basis"],
        "weather_provenance_status": manifest["provenance_status"],
        "scada_timezone_status": "inferred; offsets 5, 6, 7 compared without selecting one",
        "scada_source_sha256": source_sha,
        "coverage_rule": "unique 10-minute slots/6 == 1, no quality flags; common UTC valid hours across both turbines and all three offsets",
        "candidate_complete_hours": candidate_complete_hours,
        "common_unique_valid_hours": len(common_hours),
        "weather_issue_valid_pairs_before_common": len(weather),
        "common_issue_valid_pairs": len(common_pairs),
        "overlap_note": "A valid hour can occur in two issue forecasts; all is weighted by issue+valid pair. Lead buckets are reported separately.",
        "height_note": "NWP wind is at 100 m; SCADA anemometer height is unconfirmed, so MAE includes vertical representativeness error.",
        "metrics": metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases-dir", type=Path, required=True)
    parser.add_argument("--weather-manifest", type=Path, default=Path("artifacts/c1/weather-batch-manifest.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = analyse(args.cases_dir, args.weather_manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "common_unique_valid_hours": report["common_unique_valid_hours"],
        "common_issue_valid_pairs": report["common_issue_valid_pairs"],
        "metrics": report["metrics"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
