"""Behavioral boundaries: leakage, missing input, real export and rerun retention."""
import json
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from datetime import timedelta
from pathlib import Path
from src.ml.common import iso, utc, write_json
from src.ml.forecast import predict_forecast, WeatherUnavailable, InvalidForecastRequest, CoreNotReady
from src.agent.runner import run_forecast


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.model=self.root/"model"; self.weather=self.root/"weather"; self.weather.mkdir()
        self.request={"issue_time":"2026-02-01T12:00:00Z","turbine_ids":["turbine_1","turbine_2"],"horizon_hours":48}
        spec={"kind":"curve","curve":{"wind":[0,20],"power":[-0.1,1.3]}}
        self.manifest={"training_end_exclusive":"2026-01-31T00:00:00Z","model_version":"synthetic-test-only","scada_timezone":"UTC+6 inferred","turbines":{"turbine_1":spec,"turbine_2":spec}}
        write_json(self.model/"manifest.json",self.manifest)
        self.rows=[]
        for lead in range(1,49):
            self.rows.append({"provider":"test","model":"test","run_time":"2026-02-01T00:00:00Z","available_at":"2026-02-01T09:00:00Z","availability_basis":"inferred_run_plus_9h","provenance_status":"unconfirmed","valid_time":iso(utc(self.request["issue_time"])+timedelta(hours=lead)),"source_reference":"test-sha","variables":{"wind_speed_100m_m_s":20,"wind_direction_100m_deg":90,"temperature_2m_c":5}})
        self.save_weather()

    def tearDown(self): self.temp.cleanup()

    def save_weather(self):
        (self.weather/"2026-02-01.jsonl").write_text("\n".join(json.dumps(r) for r in self.rows),encoding="utf-8")

    def predict(self): return predict_forecast(**self.request,model_dir=self.model,weather_dir=self.weather)

    def test_complete_two_turbines_no_arbitrary_clipping(self):
        result=self.predict(); self.assertEqual(len(result["rows"]),96)
        self.assertEqual(result["rows"][0]["y_pred"],1.3)
        self.assertEqual(result["metadata"]["provenance_status"],"unconfirmed")

    def test_future_weather_rejected(self):
        self.rows[0]["available_at"]="2026-02-01T13:00:00Z"; self.save_weather()
        with self.assertRaises(WeatherUnavailable): self.predict()

    def test_incomplete_weather_rejected(self):
        self.rows.pop(); self.save_weather()
        with self.assertRaises(WeatherUnavailable): self.predict()

    def test_future_model_rejected(self):
        self.manifest["training_end_exclusive"]="2026-02-02T00:00:00Z"; write_json(self.model/"manifest.json",self.manifest)
        with self.assertRaises(InvalidForecastRequest): self.predict()

    def test_naive_time_rejected(self):
        self.request["issue_time"]="2026-02-01T12:00:00"
        with self.assertRaises(ValueError): self.predict()

    def test_rerun_preserves_both_exports_and_actual_events(self):
        events=[]
        for _ in range(2):
            result=run_forecast(self.request,events.append,model_dir=self.model,weather_dir=self.weather,output_dir=self.root/"runs",agent_mode="deterministic")
            self.assertEqual(result["mode"],"deterministic")
        self.assertEqual(len(list((self.root/"runs").glob("*/forecast.csv"))),2)
        self.assertEqual([e["tool"] for e in events if e["state"]=="ok"],["weather","prepare","forecast","validate","export"]*2)
        self.assertFalse(any(e["tool"]=="llm" for e in events))

    def test_failure_no_success_export(self):
        self.rows.pop(); self.save_weather(); events=[]
        with self.assertRaises(WeatherUnavailable): run_forecast(self.request,events.append,model_dir=self.model,weather_dir=self.weather,output_dir=self.root/"runs",agent_mode="deterministic")
        self.assertFalse(list((self.root/"runs").glob("*/forecast.csv")))
        self.assertEqual(events[-1]["state"],"error")

    def test_llm_failure_after_export_keeps_only_partial_artifacts_and_usage(self):
        class Call:
            type="function_call"
            arguments="{}"
            def __init__(self,name): self.name=name; self.call_id=name
            def model_dump(self,**kwargs): return {"type":self.type,"name":self.name,"arguments":self.arguments,"call_id":self.call_id}
        class FakeResponses:
            def __init__(self): self.index=0
            def create(self,**kwargs):
                names=["weather","prepare","forecast","validate","export"]
                if self.index==5: raise TimeoutError("synthetic failure after export")
                name=names[self.index]; self.index+=1
                return SimpleNamespace(usage=SimpleNamespace(input_tokens=100,output_tokens=20),output=[Call(name)],output_text="")
        client=SimpleNamespace(responses=FakeResponses()); events=[]
        with patch.dict("os.environ",{"OPENAI_BUDGET_LEDGER":str(self.root/"budget.json"),"OPENAI_MODEL":"gpt-4.1-mini-2025-04-14"}):
            with self.assertRaises(TimeoutError): run_forecast(self.request,events.append,model_dir=self.model,weather_dir=self.weather,output_dir=self.root/"runs",agent_mode="live",client=client)
        self.assertFalse(list((self.root/"runs").glob("*/forecast.csv")))
        self.assertEqual(len(list((self.root/"runs").glob("*/forecast.csv.partial"))),1)
        usage=json.loads(next((self.root/"runs").glob("*/usage.json")).read_text())
        self.assertEqual(usage["input_tokens"],500)
        self.assertEqual(usage["output_tokens"],100)
        self.assertTrue(usage["uncertain_request"])
        self.assertEqual(json.loads((self.root/"budget.json").read_text())["charged_or_reserved_usd"],0.2)

    def test_unknown_llm_price_fails_before_network(self):
        with patch.dict("os.environ",{"OPENAI_MODEL":"unpriced-test-model"}):
            with self.assertRaises(CoreNotReady): run_forecast(self.request,lambda event:None,model_dir=self.model,weather_dir=self.weather,output_dir=self.root/"runs",agent_mode="live",client=object())

if __name__=="__main__": unittest.main()
