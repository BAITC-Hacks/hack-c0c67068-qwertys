"""Verify a local C1 weather batch manifest and every selected JSONL row."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Missing timezone offset")
    return parsed.astimezone(timezone.utc)


def verify(manifest_path: Path, start: date, end: date) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("availability_basis") != "inferred_run_plus_9h":
        raise ValueError("Unexpected availability policy")
    failures = []
    response_bytes = 0
    current = start
    while current <= end:
        key = current.isoformat()
        entry = manifest["runs"].get(key)
        try:
            if entry is None or entry.get("status") != "ready":
                raise ValueError("Run missing or failed")
            cache = Path(entry["cache_file"])
            rows_path = Path(entry["rows_file"])
            if hashlib.sha256(cache.read_bytes()).hexdigest() != entry["source_sha256"]:
                raise ValueError("Raw response SHA mismatch")
            rows = [json.loads(line) for line in rows_path.read_text(encoding="utf-8").splitlines()]
            if len(rows) != 48 or entry["selected_hours"] != 48:
                raise ValueError("Expected 48 selected rows")
            issue = _utc(entry["issue_time"])
            available = _utc(entry["available_at"])
            if available > issue:
                raise ValueError("Run unavailable at issue time")
            for lead, row in enumerate(rows, start=1):
                if _utc(row["valid_time"]) != issue + timedelta(hours=lead):
                    raise ValueError(f"Invalid time at lead {lead}")
                if row["source_reference"] != entry["source_sha256"]:
                    raise ValueError("Row references different response SHA")
                if row["availability_basis"] != "inferred_run_plus_9h":
                    raise ValueError("Row availability policy differs")
                if row["provenance_status"] != "unconfirmed":
                    raise ValueError("Row claims confirmed provenance")
                if any(
                    isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
                    for value in row["variables"].values()
                ):
                    raise ValueError("Invalid weather value")
            response_bytes += entry["response_bytes"]
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            failures.append({"run": key, "error": str(error)})
        current += timedelta(days=1)
    requested = (end - start).days + 1
    return {
        "requested_runs": requested,
        "verified_runs": requested - len(failures),
        "selected_hours": 48 * (requested - len(failures)),
        "raw_response_bytes": response_bytes,
        "failures": failures,
        "manifest": str(manifest_path),
        "availability_basis": manifest["availability_basis"],
        "provenance_status": manifest["provenance_status"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/c1/weather-batch-manifest.json"))
    parser.add_argument("--start-date", type=date.fromisoformat, required=True)
    parser.add_argument("--end-date", type=date.fromisoformat, required=True)
    args = parser.parse_args()
    result = verify(args.manifest, args.start_date, args.end_date)
    print(json.dumps(result, ensure_ascii=False))
    if result["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
