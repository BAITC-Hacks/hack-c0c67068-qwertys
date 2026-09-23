"""Fetch a bounded date range of daily ECMWF runs for C2.

One 00Z run per day, issue at 12Z, 48-hour horizon. Raw responses and
JSONL rows stay in Git-ignored local directories; a small manifest records
SHA, coverage and provenance. The manifest is updated after each run, so a
partial download is immediately usable and the command can be resumed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .open_meteo import build_url, inspect_payload, probe, select_horizon

LATITUDE = 43.645150
LONGITUDE = 78.535604


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary.replace(path)


def _cache_valid(entry: dict) -> bool:
    cache_file = Path(entry.get("cache_file", ""))
    rows_file = Path(entry.get("rows_file", ""))
    if not cache_file.is_file() or not rows_file.is_file():
        return False
    digest = hashlib.sha256(cache_file.read_bytes()).hexdigest()
    return digest == entry.get("source_sha256") and entry.get("selected_hours") == 48


def fetch_range(
    start: date,
    end: date,
    cache_dir: Path,
    output_dir: Path,
    manifest_path: Path,
    *,
    sleep_seconds: float = 1.0,
    cached_response: Path | None = None,
) -> dict:
    if end < start or (end - start).days > 124:
        raise ValueError("Range must be nonempty and at most 125 daily runs")
    if sleep_seconds < 1.0:
        raise ValueError("Minimum interval between request starts is 1.0 second")
    if cached_response is not None and start != end:
        raise ValueError("--cached-response requires a single run date")
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "schema_version": 1,
            "provider": "Open-Meteo Single Runs",
            "model": "ecmwf_ifs",
            "location": {"latitude": LATITUDE, "longitude": LONGITUDE},
            "run_rule": "daily 00:00Z",
            "issue_rule": "same date 12:00Z",
            "horizon_hours": 48,
            "availability_basis": "inferred_run_plus_9h",
            "provenance_status": "unconfirmed",
            "runs": {},
        }
    manifest["source_terms"] = "CC BY 4.0 data; free Open-Meteo API for non-commercial use only"
    manifest["source_terms_url"] = "https://open-meteo.com/en/terms"
    manifest["attribution"] = "Weather data: Open-Meteo.com; underlying model: ECMWF IFS"
    manifest["units"] = {"wind_speed_100m_m_s": "m/s", "wind_direction_100m_deg": "degrees", "temperature_2m_c": "°C"}
    manifest["model_cycle_note"] = "IFS 49r1 became operational 2024-11-12; older archive responses are hindcasts. Later as-issued publication remains unconfirmed."
    for run_day, entry in manifest["runs"].items():
        if entry.get("status") == "ready":
            entry.setdefault("expected_hours", 48)
            entry.setdefault("missing_selected_hours", 0)
            entry.setdefault("missing_selected_values", 0)
            entry["model_cycle_regime"] = "hindcast_pre_operational_49r1" if run_day < "2024-11-12" else "operational_epoch_publication_unconfirmed"
    current = start
    attempted = 0
    while current <= end:
        key = current.isoformat()
        existing = manifest["runs"].get(key, {})
        if existing.get("status") == "ready" and _cache_valid(existing):
            current += timedelta(days=1)
            continue
        run = key + "T00:00Z"
        issue = key + "T12:00Z"
        last_error = None
        request_started = time.monotonic()
        for attempt in range(1 if cached_response is not None else 3):
            try:
                if cached_response is not None:
                    cache_file = cached_response
                    payload = cache_file.read_bytes()
                    url = build_url(LATITUDE, LONGITUDE, run, forecast_hours=72)
                    rows, report = inspect_payload(payload, url=url, run=run)
                    if cache_file.stem != report["response_sha256"]:
                        raise ValueError("Cached response filename and SHA differ")
                else:
                    rows, report, cache_file = probe(
                        LATITUDE, LONGITUDE, run, cache_dir, forecast_hours=72
                    )
                selected = select_horizon(rows, issue, 48)
                if len(selected) != 48:
                    raise ValueError("Expected exactly 48 selected weather hours")
                rows_file = output_dir / (key + ".jsonl")
                _write_jsonl(rows_file, selected)
                manifest["runs"][key] = {
                    "status": "ready",
                    "run_time": selected[0]["run_time"],
                    "issue_time": issue,
                    "available_at": selected[0]["available_at"],
                    "availability_basis": selected[0]["availability_basis"],
                    "provenance_status": selected[0]["provenance_status"],
                    "model_cycle_regime": "hindcast_pre_operational_49r1" if key < "2024-11-12" else "operational_epoch_publication_unconfirmed",
                    "first_valid_time": selected[0]["valid_time"],
                    "last_valid_time": selected[-1]["valid_time"],
                    "selected_hours": len(selected),
                    "expected_hours": 48,
                    "missing_selected_hours": 0,
                    "missing_selected_values": 0,
                    "source_sha256": report["response_sha256"],
                    "response_bytes": report["response_bytes"],
                    "source_url": report["source_url"],
                    "grid_latitude": report["grid_latitude"],
                    "grid_longitude": report["grid_longitude"],
                    "null_counts": report["null_counts"],
                    "cache_file": str(cache_file),
                    "rows_file": str(rows_file),
                }
                last_error = None
                break
            except Exception as error:
                last_error = f"{type(error).__name__}: {error}"
                if attempt < 2:
                    time.sleep(2 ** attempt)
        if last_error is not None:
            manifest["runs"][key] = {"status": "failed", "run_time": run, "error": last_error}
        manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        _write_json(manifest_path, manifest)
        attempted += 1
        if attempted == 1 or attempted % 10 == 0 or last_error:
            ready = sum(v.get("status") == "ready" for v in manifest["runs"].values())
            failed = sum(v.get("status") == "failed" for v in manifest["runs"].values())
            print(f"{key}: {manifest['runs'][key]['status']} | ready={ready} failed={failed}", flush=True)
        if current < end:
            time.sleep(max(0.0, sleep_seconds - (time.monotonic() - request_started)))
        current += timedelta(days=1)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-date", type=date.fromisoformat, required=True)
    parser.add_argument("--end-date", type=date.fromisoformat, required=True)
    parser.add_argument("--cache-dir", type=Path, default=Path("data/cache/weather"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/c1/weather_runs"))
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/c1/weather-batch-manifest.json"))
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument("--cached-response", type=Path, help="For a single run, ingest an existing SHA-named JSON without HTTP")
    args = parser.parse_args()
    manifest = fetch_range(
        args.start_date, args.end_date, args.cache_dir, args.output_dir, args.manifest,
        sleep_seconds=args.sleep_seconds,
        cached_response=args.cached_response,
    )
    total = (args.end_date - args.start_date).days + 1
    scoped = [manifest["runs"].get((args.start_date + timedelta(days=i)).isoformat(), {}) for i in range(total)]
    ready = sum(entry.get("status") == "ready" for entry in scoped)
    failed = total - ready
    print(json.dumps({"requested": total, "ready": ready, "failed": failed, "manifest": str(args.manifest)}))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
