"""Turn the supplied 10-minute SCADA files into hourly observations.

SCADA timestamps are treated as a fixed UTC+6 clock *hypothesis*, not
verified sensor metadata. The offset is an explicit argument.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

TIME = "Статистическое время"
WIND = "Средняя скорость ветра(m/s)"
POWER = "Нормализованная активная мощность"
TEMP = "Средняя температура окружающей среды(°C)"
REQUIRED = {TIME, WIND, POWER, TEMP}


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_hourly(
    path: Path,
    turbine_id: str,
    *,
    utc_offset_hours: int = 6,
    start_utc: datetime | None = None,
    end_utc: datetime | None = None,
) -> tuple[list[dict], dict]:
    if not -12 <= utc_offset_hours <= 14:
        raise ValueError("utc_offset_hours outside plausible UTC offset range")
    if turbine_id not in ("turbine_1", "turbine_2"):
        raise ValueError("turbine_id must be turbine_1 or turbine_2")
    path = Path(path)
    buckets: dict[datetime, list[tuple[datetime, float, float, float]]] = defaultdict(list)
    raw_rows = 0
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing SCADA columns: {sorted(missing)}")
        for line_no, record in enumerate(reader, start=2):
            raw_rows += 1
            try:
                local = datetime.strptime(record[TIME], "%Y-%m-%d %H:%M:%S")
                wind = float(record[WIND])
                power = float(record[POWER])
                temp = float(record[TEMP])
                if not all(math.isfinite(x) for x in (wind, power, temp)):
                    raise ValueError("nonfinite numeric value")
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid SCADA row {line_no}: {error}") from error
            utc = (local - timedelta(hours=utc_offset_hours)).replace(tzinfo=timezone.utc)
            hour = utc.replace(minute=0, second=0, microsecond=0)
            if start_utc is not None and hour < start_utc:
                continue
            if end_utc is not None and hour >= end_utc:
                continue
            buckets[hour].append((utc, wind, temp, power))

    result = []
    for hour, readings in sorted(buckets.items()):
        stamps = [reading[0] for reading in readings]
        unique = set(stamps)
        expected = {hour + timedelta(minutes=10 * i) for i in range(6)}
        valid = [reading for reading in readings if reading[0] in expected]
        flags = []
        if len(unique) != len(stamps):
            flags.append("duplicate_timestamp")
        if set(stamps) - expected:
            flags.append("off_grid_timestamp")
        if len({reading[0] for reading in valid}) < 6:
            flags.append("partial_hour")
        # Duplicate readings are not silently averaged twice.
        by_time = {reading[0]: reading for reading in valid}
        values = list(by_time.values())
        if not values:
            continue
        result.append({
            "turbine_id": turbine_id,
            "timestamp": _iso(hour),
            "timezone_interpretation": f"fixed UTC+{utc_offset_hours} hypothesis",
            "timezone_status": "inferred",
            "utc_offset_hours": utc_offset_hours,
            "wind_m_s": sum(v[1] for v in values) / len(values),
            "temperature_c": sum(v[2] for v in values) / len(values),
            "power_normalized": sum(v[3] for v in values) / len(values),
            "coverage": len(values) / 6,
            "quality_flags": flags,
        })
    report = {
        "source_name": path.name,
        "source_sha256": file_sha256(path),
        "turbine_id": turbine_id,
        "raw_rows": raw_rows,
        "output_hours": len(result),
        "complete_hours": sum(row["coverage"] == 1 and not row["quality_flags"] for row in result),
        "partial_hours": sum("partial_hour" in row["quality_flags"] for row in result),
        "first_hour_utc": result[0]["timestamp"] if result else None,
        "last_hour_utc": result[-1]["timestamp"] if result else None,
        "timezone_hypothesis": f"fixed UTC+{utc_offset_hours}",
        "timezone_status": "inferred",
        "utc_offset_hours": utc_offset_hours,
        "aggregation": "arithmetic mean of unique on-grid 10-minute readings; coverage=unique slots/6",
        "start_utc": _iso(start_utc) if start_utc else None,
        "end_utc_exclusive": _iso(end_utc) if end_utc else None,
    }
    return result, report


def _parse_utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("UTC input must include Z or +00:00")
    return parsed.astimezone(timezone.utc)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--turbine-id", required=True)
    parser.add_argument("--utc-offset-hours", type=int, default=6)
    parser.add_argument("--start-utc", help="Inclusive UTC ISO time")
    parser.add_argument("--end-utc", help="Exclusive UTC ISO time")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    rows, report = prepare_hourly(
        args.input,
        args.turbine_id,
        utc_offset_hours=args.utc_offset_hours,
        start_utc=_parse_utc(args.start_utc),
        end_utc=_parse_utc(args.end_utc),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "report": str(args.report), **report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
