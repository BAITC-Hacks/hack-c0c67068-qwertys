import csv
import json
import tempfile
import unittest
from datetime import datetime, timezone
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
            rows, report = prepare_hourly(path, "turbine_1", utc_offset_hours=6)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["timestamp"], "2026-01-30T18:00:00Z")
        self.assertEqual(rows[0]["timezone_status"], "inferred")
        self.assertEqual(rows[0]["coverage"], 2 / 6)
        self.assertEqual(rows[0]["wind_m_s"], 5)
        self.assertIn("duplicate_timestamp", rows[0]["quality_flags"])
        self.assertIn("partial_hour", rows[0]["quality_flags"])
        self.assertEqual(report["raw_rows"], 3)


class WeatherSourceTests(unittest.TestCase):
    def test_source_hash_and_issue_time_gate(self):
        hourly = {
            "time": [f"2026-01-31T{hour:02d}:00" for hour in range(24)],
            "wind_speed_100m": [5.0] * 24,
            "wind_direction_100m": [90] * 24,
            "temperature_2m": [1.0] * 24,
        }
        payload = json.dumps({"hourly": hourly}).encode()
        rows, report = inspect_payload(payload, url="https://example.test/run", run="2026-01-31T00:00Z")
        self.assertEqual(report["hour_count"], 24)
        self.assertEqual(report["null_counts"]["wind_speed_100m"], 0)
        self.assertEqual(rows[0]["available_at"], "2026-01-31T06:00:00Z")
        self.assertEqual(rows[0]["provenance_status"], "unconfirmed")
        with self.assertRaisesRegex(ValueError, "unavailable"):
            select_horizon(rows, "2026-01-31T00:00Z", 24)
        with self.assertRaisesRegex(ValueError, "does not cover"):
            select_horizon(rows, "2026-01-31T07:00Z", 24)


if __name__ == "__main__":
    unittest.main()
