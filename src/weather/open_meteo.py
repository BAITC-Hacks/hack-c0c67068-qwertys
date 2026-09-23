"""Small, auditable Open-Meteo Single Runs source probe and adapter.

The API's `run` is model initialization, not publication. A +9 h
availability rule is an operational safety-margin hypothesis, not source metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ENDPOINT = "https://single-runs-api.open-meteo.com/v1/forecast"
HOURLY = "wind_speed_100m,wind_direction_100m,temperature_2m"
PROVIDER_DOC = "https://open-meteo.com/en/docs/single-runs-api"
AVAILABILITY_LAG_HOURS = 9
EXPECTED_UPSTREAM_UNITS = {
    "time": "iso8601",
    "wind_speed_100m": "m/s",
    "wind_direction_100m": "°",
    "temperature_2m": "°C",
}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Time must include UTC offset")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def build_url(latitude: float, longitude: float, run: str, forecast_hours: int = 72) -> str:
    if forecast_hours not in (24, 48, 72):
        raise ValueError("Probe is limited to 24, 48 or 72 hours")
    run_time = _parse_utc(run)
    query = {
        "latitude": f"{latitude:.6f}",
        "longitude": f"{longitude:.6f}",
        "hourly": HOURLY,
        "run": run_time.strftime("%Y-%m-%dT%H:%M"),
        "forecast_hours": str(forecast_hours),
        "timezone": "GMT",
        "models": "ecmwf_ifs",
        "wind_speed_unit": "ms",
    }
    return ENDPOINT + "?" + urlencode(query)


def inspect_payload(payload: bytes, *, url: str, run: str) -> tuple[dict, dict]:
    response = json.loads(payload)
    if response.get("error"):
        raise ValueError(f"Provider error: {response.get('reason', 'unknown')}")
    hourly = response["hourly"]
    names = ("wind_speed_100m", "wind_direction_100m", "temperature_2m")
    times = hourly["time"]
    if not times or any(len(hourly[name]) != len(times) for name in names):
        raise ValueError("Weather arrays have inconsistent lengths")
    if len(set(times)) != len(times):
        raise ValueError("Weather timestamps are duplicated")
    hourly_units = response.get("hourly_units")
    if not isinstance(hourly_units, dict):
        raise ValueError("Missing or invalid provider hourly_units")
    for name, expected in EXPECTED_UPSTREAM_UNITS.items():
        actual = hourly_units.get(name)
        if actual != expected:
            raise ValueError(f"Unexpected provider unit for {name}: expected {expected!r}, got {actual!r}")
    run_time = _parse_utc(run)
    sha = hashlib.sha256(payload).hexdigest()
    available_at = run_time + timedelta(hours=AVAILABILITY_LAG_HOURS)
    weather_rows = []
    for index, raw_time in enumerate(times):
        valid_time = datetime.fromisoformat(raw_time)
        valid_time = valid_time.replace(tzinfo=timezone.utc) if valid_time.tzinfo is None else valid_time.astimezone(timezone.utc)
        if index and valid_time != _parse_utc(weather_rows[-1]["valid_time"]) + timedelta(hours=1):
            raise ValueError("Weather times are not consecutive hourly values")
        weather_rows.append({
            "provider": "Open-Meteo Single Runs",
            "model": "ecmwf_ifs",
            "run_time": _iso(run_time),
            "available_at": _iso(available_at),
            "available_at_basis": "inferred run_init + 9h safety margin; not provider publication timestamp",
            "availability_basis": "inferred_run_plus_9h",
            "provenance_status": "unconfirmed",
            "valid_time": _iso(valid_time),
            "variables": {
                "wind_speed_100m_m_s": hourly["wind_speed_100m"][index],
                "wind_direction_100m_deg": hourly["wind_direction_100m"][index],
                "temperature_2m_c": hourly["temperature_2m"][index],
            },
            "units": {"wind_speed_100m_m_s": "m/s", "wind_direction_100m_deg": "degrees", "temperature_2m_c": "°C"},
            "source_reference": sha,
        })
    report = {
        "source_url": url,
        "provider_documentation": PROVIDER_DOC,
        "response_sha256": sha,
        "response_bytes": len(payload),
        "run_init_utc": _iso(run_time),
        "available_at_utc_assumed": _iso(available_at),
        "availability_status": "ASSUMED, not verified historical publication",
        "availability_basis": "inferred_run_plus_9h",
        "provenance_status": "unconfirmed",
        "model": "ecmwf_ifs",
        "grid_latitude": response.get("latitude"),
        "grid_longitude": response.get("longitude"),
        "grid_elevation_m": response.get("elevation"),
        "hour_count": len(times),
        "first_valid_time": weather_rows[0]["valid_time"],
        "last_valid_time": weather_rows[-1]["valid_time"],
        "null_counts": {name: sum(value is None for value in hourly[name]) for name in names},
        "hourly_units": hourly_units,
        "provenance_limit": "HTTP response and cycle date do not prove as-issued operational field at historical issue time",
    }
    return weather_rows, report


def probe(
    latitude: float,
    longitude: float,
    run: str,
    cache_dir: Path,
    *,
    forecast_hours: int = 72,
) -> tuple[list[dict], dict, Path]:
    url = build_url(latitude, longitude, run, forecast_hours)
    request = Request(url, headers={"User-Agent": "HackAlem-C1-source-probe/1.0"})
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError(f"HTTP {response.status}")
        payload = response.read(2_000_001)
    if len(payload) > 2_000_000:
        raise ValueError("Probe response exceeds 2 MB limit")
    rows, report = inspect_payload(payload, url=url, run=run)
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / (report["response_sha256"] + ".json")
    cache_file.write_bytes(payload)
    report["cache_file"] = str(cache_file)
    report["retrieved_at_utc"] = _iso(datetime.now(timezone.utc))
    return rows, report, cache_file


def select_horizon(rows: list[dict], issue_time: str, horizon_hours: int) -> list[dict]:
    if horizon_hours not in (24, 48):
        raise ValueError("Horizon must be 24 or 48 hours")
    issue = _parse_utc(issue_time)
    target = [_iso(issue + timedelta(hours=i)) for i in range(1, horizon_hours + 1)]
    if not rows:
        raise ValueError("Weather run has no rows")
    by_valid = {}
    cycle = None
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Weather row must be an object")
        required = {
            "provider", "model", "run_time", "available_at", "valid_time",
            "variables", "units", "source_reference", "availability_basis",
            "provenance_status",
        }
        missing = required - row.keys()
        if missing:
            raise ValueError(f"Missing weather row keys: {sorted(missing)}")
        if not all(isinstance(row[key], str) and row[key] for key in ("provider", "model", "source_reference", "availability_basis", "provenance_status")):
            raise ValueError("Weather source identity is empty")
        run_time = _iso(_parse_utc(row["run_time"]))
        available_at = _iso(_parse_utc(row["available_at"]))
        valid_time = _iso(_parse_utc(row["valid_time"]))
        if _parse_utc(run_time) > _parse_utc(available_at):
            raise ValueError("Run initialization is after availability")
        identity = (
            row["provider"], row["model"], run_time, available_at,
            row["source_reference"], row["availability_basis"],
            row["provenance_status"],
        )
        if cycle is None:
            cycle = identity
        elif identity != cycle:
            raise ValueError("Mixed weather run cycles or source references")
        if valid_time in by_valid:
            raise ValueError(f"Duplicate weather valid_time: {valid_time}")
        by_valid[valid_time] = row
    selected = []
    for valid in target:
        row = by_valid.get(valid)
        if row is None:
            raise ValueError(f"Weather run does not cover {valid}")
        if _parse_utc(row["available_at"]) > issue:
            raise ValueError("Run unavailable under the +9h availability assumption")
        if not isinstance(row["variables"], dict) or not isinstance(row["units"], dict):
            raise ValueError(f"Weather variables/units must be objects at {valid}")
        expected_units = {
            "wind_speed_100m_m_s": "m/s",
            "wind_direction_100m_deg": "degrees",
            "temperature_2m_c": "°C",
        }
        missing_vars = expected_units.keys() - row["variables"].keys()
        if missing_vars:
            raise ValueError(f"Missing weather variables at {valid}: {sorted(missing_vars)}")
        if any(row["units"].get(key) != unit for key, unit in expected_units.items()):
            raise ValueError(f"Unexpected weather units at {valid}")
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
            for value in (row["variables"][key] for key in expected_units)
        ):
            raise ValueError(f"Nonfinite or nonnumeric weather variable at {valid}")
        if row["variables"]["wind_speed_100m_m_s"] < 0:
            raise ValueError(f"Negative wind speed at {valid}")
        if row["variables"]["temperature_2m_c"] < -273.15:
            raise ValueError(f"Temperature below absolute zero at {valid}")
        if not 0 <= row["variables"]["wind_direction_100m_deg"] <= 360:
            raise ValueError(f"Wind direction outside 0..360 degrees at {valid}")
        selected.append(row)
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True)
    parser.add_argument("--run", required=True, help="Initialization UTC ISO, e.g. 2026-01-31T00:00Z")
    parser.add_argument("--forecast-hours", type=int, default=72)
    parser.add_argument("--cache-dir", type=Path, default=Path("data/cache/weather"))
    parser.add_argument("--cached-response", type=Path, help="Replay a previously fetched JSON response without network")
    parser.add_argument("--issue-time", help="Optional UTC issue time for 24/48-hour selection")
    parser.add_argument("--horizon-hours", type=int, choices=(24, 48), default=48)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Optional JSONL of hourly fields")
    args = parser.parse_args()
    if args.cached_response:
        payload = args.cached_response.read_bytes()
        url = build_url(args.latitude, args.longitude, args.run, args.forecast_hours)
        rows, report = inspect_payload(payload, url=url, run=args.run)
        report["cache_file"] = str(args.cached_response)
        report["mode"] = "offline replay"
    else:
        rows, report, _ = probe(args.latitude, args.longitude, args.run, args.cache_dir, forecast_hours=args.forecast_hours)
        report["mode"] = "live fetch"
    if args.issue_time:
        rows = select_horizon(rows, args.issue_time, args.horizon_hours)
        report["issue_time_utc"] = _iso(_parse_utc(args.issue_time))
        report["selected_hours"] = len(rows)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="\n") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"report": str(args.report), **report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
