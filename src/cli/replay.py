"""Sequential daily issue replay, preserving overlaps and an explicit final rule."""
from __future__ import annotations
import argparse
import csv
import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
from src.agent.runner import run_forecast
from src.ml.common import TURBINES,iso,utc,write_json


def replay(*,model_dir=None,weather_dir=None,output_dir="artifacts/replay",target_offset_hours=6,min_lead_hours=1):
    if min_lead_hours not in (1,24): raise ValueError("Supported export minimum leads:1 or24")
    directory=Path(output_dir)/uuid4().hex; directory.mkdir(parents=True)
    target_start=datetime(2026,2,1,tzinfo=timezone(timedelta(hours=target_offset_hours))).astimezone(timezone.utc)
    target_end=datetime(2026,3,1,tzinfo=timezone(timedelta(hours=target_offset_hours))).astimezone(timezone.utc)
    issue=(target_start-timedelta(hours=min_lead_hours)).replace(hour=12,minute=0,second=0,microsecond=0)
    if issue>target_start-timedelta(hours=min_lead_hours): issue-=timedelta(days=1)
    journal=[]; runs=[]
    summary={"status":"running","target_start_utc":iso(target_start),"target_end_exclusive_utc":iso(target_end),"calendar_offset_hours":target_offset_hours,"timezone_status":"inferred","selection_status":"proposed_not_confirmed_by_organizer","rule":f"For each turbine/target hour select newest issue among stored forecasts with lead_hours>={min_lead_hours}. Preserve all original issue/target rows separately.","min_lead_hours":min_lead_hours,"february_metrics":None,"provenance_status":"unconfirmed"}
    write_json(directory/"manifest.json",summary)
    try:
        while True:
            events=[]
            payload=run_forecast({"issue_time":iso(issue),"turbine_ids":list(TURBINES),"horizon_hours":48},events.append,model_dir=model_dir,weather_dir=weather_dir,output_dir=directory/"runs",agent_mode="deterministic")
            run_id=json.loads(next(e["summary"] for e in events if e["tool"]=="export" and e["state"]=="ok"))["export_id"]
            rows=[{"run_id":run_id,**row,"unit":"normalized_power",**payload["metadata"]} for row in payload["rows"]]
            journal.extend(rows); runs.append({"run_id":run_id,"issue_time":iso(issue),"rows":len(rows),"model_version":payload["metadata"]["model_version"],"input_version":payload["metadata"]["input_version"]})
            if issue+timedelta(hours=48)>=target_end-timedelta(hours=1): break
            issue+=timedelta(days=1)
        selected={}
        for row in journal:
            if target_start<=utc(row["valid_time"])<target_end and row["lead_hours"]>=min_lead_hours:
                key=(row["turbine_id"],row["valid_time"])
                if key not in selected or row["issue_time"]>selected[key]["issue_time"]: selected[key]=row
        for turbine in TURBINES:
            for h in range(672):
                if (turbine,iso(target_start+timedelta(hours=h))) not in selected: raise ValueError("Final February export has a missing target hour")
        final=[selected[key] for key in sorted(selected)]
        for name,rows in (("all-issues.csv",journal),("february.csv",final)):
            with (directory/name).open("w",encoding="utf-8-sig",newline="") as stream:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        summary.update({"status":"completed","runs":runs,"full_journal_rows":len(journal),"unique_february_rows":len(final),"hours_per_turbine":672,"mode":"deterministic"})
        write_json(directory/"manifest.json",summary)
        return directory,summary
    except Exception:
        summary.update({"status":"failed","completed_runs":runs})
        write_json(directory/"manifest.json",summary)
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir"); parser.add_argument("--weather-dir")
    parser.add_argument("--output-dir",default="artifacts/replay")
    parser.add_argument("--target-offset-hours",type=int,default=6)
    parser.add_argument("--min-lead-hours",type=int,choices=(1,24),default=1,help="24 requires a model trained before the earlier warm-start issue; default uses all leads1..48")
    args=parser.parse_args(); directory,summary=replay(**vars(args))
    print(json.dumps({"output":str(directory),"status":summary["status"],"runs":len(summary["runs"]),"full_journal_rows":summary["full_journal_rows"],"unique_february_rows":summary["unique_february_rows"]}))

if __name__=="__main__": main()
