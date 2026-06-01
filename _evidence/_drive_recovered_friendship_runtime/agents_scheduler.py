
from datetime import datetime, timezone
import threading, time
from app.meta.agents_unified_runtime import run_agent
import json

def _run_loop():
    while True:
        try:
            agents = json.load(open('app/meta/agents_registry.json'))['agents']
            for ag in agents:
                if ag.get('governance', {}).get('auto_run'):
                    run_agent(ag['id'], payload={'auto': True})
        except Exception:
            pass
        time.sleep(5)

def start_scheduler():
    th = threading.Thread(target=_run_loop, daemon=True)
    th.start()
