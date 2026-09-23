"""Launch the local product with explicit deterministic mode by default."""
import argparse
import os
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    os.chdir(root)
    from dotenv import load_dotenv
    load_dotenv(root / '.env', override=False)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--model-dir', default=os.getenv('MODEL_DIR', 'models/production'))
    parser.add_argument('--weather-dir', default=os.getenv('WEATHER_RUNS_DIR', 'artifacts/c1/weather_runs'))
    parser.add_argument('--ui-dir', type=Path, default=Path('web/dist'))
    parser.add_argument('--agent-mode', choices=('deterministic', 'live'), default='deterministic')
    parser.add_argument('--check', action='store_true', help='Check model/cache readiness without starting a server')
    args = parser.parse_args()
    os.environ.update(MODEL_DIR=str(args.model_dir), WEATHER_RUNS_DIR=str(args.weather_dir), AGENT_MODE=args.agent_mode,
                      FORECAST_RUNNER='src.agent.runner:run_forecast')
    from src.agent.runner import readiness, run_forecast
    state = readiness()
    if not state.get('ready'):
        print('Not ready: ' + state.get('reason', 'model or weather configuration unavailable'))
        print('Follow README: copy/train the model, prepare the weather cache, then run this command again.')
        return 1
    if args.check:
        print(f"Ready: {state.get('model_version', 'model')} / mode={args.agent_mode}; date coverage checked per request")
        return 0
    if not args.ui_dir.is_dir():
        print('UI build absent. Run npm.cmd ci and npm.cmd run build in web/, or start the Vite dev server.')
    from src.api.main import create_app
    import uvicorn
    print(f'Local product: http://{args.host}:{args.port} / mode={args.agent_mode}')
    uvicorn.run(create_app(run_forecast, static_dir=args.ui_dir, readiness=readiness), host=args.host, port=args.port)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
