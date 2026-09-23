from __future__ import annotations
import argparse
import json
from src.agent.runner import run_forecast

def main():
    parser=argparse.ArgumentParser(description="Run a real numerical wind forecast with a bounded agent")
    parser.add_argument("--issue-time",required=True)
    parser.add_argument("--horizon-hours",type=int,choices=(24,48),default=48)
    parser.add_argument("--turbine-ids",nargs="+",default=["turbine_1","turbine_2"])
    parser.add_argument("--model-dir")
    parser.add_argument("--weather-dir")
    parser.add_argument("--output-dir")
    parser.add_argument("--agent-mode",choices=("auto","live","deterministic"),help="Overrides AGENT_MODE; otherwise environment or auto")
    args=parser.parse_args()
    def emit(event): print(json.dumps(event,ensure_ascii=True))
    try:
        payload=run_forecast({"issue_time":args.issue_time,"turbine_ids":args.turbine_ids,"horizon_hours":args.horizon_hours},emit,model_dir=args.model_dir,weather_dir=args.weather_dir,output_dir=args.output_dir,agent_mode=args.agent_mode)
    except Exception as error:
        print(json.dumps({"status":"failed","error_type":type(error).__name__}))
        raise SystemExit(1) from None
    print(json.dumps({"status":"completed","rows":len(payload["rows"]),"mode":payload["mode"],"metadata":payload["metadata"]}))

if __name__=="__main__": main()
