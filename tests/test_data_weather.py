import csv
import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.data.scada import prepare_hourly
from src.weather.open_meteo import inspect_payload, select_horizon


class ScadaPreparationTests(unittest.TestCase):
    def test_coverage_and_fixed_offset_are_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "turbine.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow([
                    "Статистическое время",
                    "Средняя скорость ветра(m/s)",
                    "Нормализованная активная мощность",
                    "Средняя температура окружающей среды(°C)",
                ])
                writer.writerow(["2026-01-31 0:00:00", 4, 0.2, 10])
                writer.writerow(["2026-01-31 0:10:00", 6, 0.4, 12])
                writer.writerow(["2026-01-31 0:10:00", 6, 0.4, 12])
                writer.writerow(["2026-01-31 0:40:00", "not-a-number", 1.0, 100])
            rows, report = prepare_hourly(
                path,
                "turbine_1",
                utc_offset_hours=6,
                end_utc=datetime(2026, 1, 30, 18, 30, tzinfo=timezone.utc),
            )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["timestamp"], "2026-01-30T18:00:00Z")
        self.assertEqual(rows[0]["timezone_status"], "inferred")
        self.assertEqual(rows[0]["coverage"], 2 / 6)
        self.assertEqual(rows[0]["wind_m_s"], 5)
        self.assertIn("duplicate_timestamp", rows[0]["quality_flags"])
        self.assertIn("partial_hour", rows[0]["quality_flags"])
        self.assertEqual(report["raw_rows"], 4)


class WeatherSourceTests(unittest.TestCase):
    def test_source_hash_and_issue_time_gate(self):
        hourly = {
            "time": [(datetime(2026, 1, 31, tzinfo=timezone.utc) + timedelta(hours=hour)).strftime("%Y-%m-%dT%H:%M") for hour in range(72)],
            "wind_speed_100m": [5.0] * 72,
            "wind_direction_100m": [90] * 72,
            "temperature_2m": [1.0] * 72,
        }
        payload = json.dumps({"hourly": hourly}).encode()
        rows, report = inspect_payload(payload, url="https://example.test/run", run="2026-01-31T00:00Z")
        self.assertEqual(report["hour_count"], 72)
        self.assertEqual(report["null_counts"]["wind_speed_100m"], 0)
        self.assertEqual(rows[0]["available_at"], "2026-01-31T09:00:00Z")
        self.assertEqual(rows[0]["provenance_status"], "unconfirmed")
        with self.assertRaisesRegex(ValueError, "unavailable"):
            select_horizon(rows, "2026-01-31T00:00Z", 24)
        with self.assertRaisesRegex(ValueError, "unavailable"):
            select_horizon(rows, "2026-01-31T06:00Z", 24)
        with self.assertRaisesRegex(ValueError, "unavailable"):
            select_horizon(rows, "2026-01-31T08:00Z", 24)
        self.assertEqual(len(select_horizon(rows, "2026-01-31T12:00Z", 48)), 48)
        with self.assertRaisesRegex(ValueError, "does not cover"):
            select_horizon(rows, "2026-02-02T12:00Z", 24)
        rows[13]["variables"]["wind_speed_100m_m_s"] = float("nan")
        with self.assertRaisesRegex(ValueError, "Nonfinite"):
            select_horizon(rows, "2026-01-31T12:00Z", 24)

    def test_select_horizon_fails_closed_on_physics_schema_and_cycles(self):
        hourly = {
            "time": [(datetime(2026, 1, 31, tzinfo=timezone.utc) + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(72)],
            "wind_speed_100m": [5.0] * 72,
            "wind_direction_100m": [90.0] * 72,
            "temperature_2m": [1.0] * 72,
        }
        rows, _ = inspect_payload(json.dumps({"hourly": hourly}).encode(), url="https://example.test/run", run="2026-01-31T00:00Z")
        issue = "2026-01-31T12:00Z"
        self.assertEqual(len(select_horizon(rows, issue, 24)), 24)
        for variable, value, error in (
            ("wind_speed_100m_m_s", -0.01, "Negative wind"),
            ("temperature_2m_c", -273.16, "absolute zero"),
            ("wind_direction_100m_deg", -1, "direction outside"),
            ("wind_direction_100m_deg", 361, "direction outside"),
        ):
            with self.subTest(variable=variable, value=value):
                bad = copy.deepcopy(rows)
                bad[13]["variables"][variable] = value
                with self.assertRaisesRegex(ValueError, error):
                    select_horizon(bad, issue, 24)
        boundary = copy.deepcopy(rows)
        boundary[13]["variables"]["wind_direction_100m_deg"] = 360
        self.assertEqual(len(select_horizon(boundary, issue, 24)), 24)
        missing_variable = copy.deepcopy(rows)
        del missing_variable[13]["variables"]["wind_speed_100m_m_s"]
        with self.assertRaisesRegex(ValueError, "Missing weather variables"):
            select_horizon(missing_variable, issue, 24)
        missing_reference = copy.deepcopy(rows)
        del missing_reference[13]["source_reference"]
        with self.assertRaisesRegex(ValueError, "Missing weather row keys"):
            select_horizon(missing_reference, issue, 24)
        mixed_cycle = copy.deepcopy(rows)
        mixed_cycle[60]["run_time"] = "2026-01-30T00:00Z"
        with self.assertRaisesRegex(ValueError, "Mixed weather run cycles"):
            select_horizon(mixed_cycle, issue, 24)
        duplicate_time = copy.deepcopy(rows)
        duplicate_time[60]["valid_time"] = duplicate_time[59]["valid_time"]
        with self.assertRaisesRegex(ValueError, "Duplicate weather valid_time"):
            select_horizon(duplicate_time, issue, 24)


if __name__ == "__main__":
    unittest.main()
