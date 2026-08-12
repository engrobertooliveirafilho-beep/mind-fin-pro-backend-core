import json, shutil
from pathlib import Path
from datetime import datetime, UTC

SRC = Path("reports/P1501_EDGE_EVOLUTION_LIVE_MONITOR/latest_edge_evolution_monitor.json")
OUT = Path("reports/P1502_DELTA_DAILY_EVOLUTION_MONITOR")
BASE = OUT / "baseline_snapshot.json"
LATEST = OUT / "latest_delta_report.json"

OUT.mkdir(parents=True, exist_ok=True)

def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def delta(now, old, key):
    return int(now.get(key) or 0) - int(old.get(key) or 0)

now = load(SRC)
old = load(BASE)

if not old:
    shutil.copyfile(SRC, BASE)
    report = {
        "STATUS": "P1502_BASELINE_CREATED",
        "MESSAGE": "Primeiro snapshot salvo. Delta real começa na próxima execução.",
        "BASELINE_AT": datetime.now(UTC).isoformat()
    }
else:
    report = {
        "STATUS": "P1502_DELTA_DAILY_EVOLUTION_MONITOR_COMPLETED",
        "DELTA_WEB_INPUTS": delta(now, old, "DISCOVERED_RESEARCH_INPUTS"),
        "DELTA_STRATEGIES_GENERATED": delta(now, old, "AUTO_STRATEGIES_GENERATED_TODAY"),
        "DELTA_BACKTESTS": delta(now, old, "BACKTESTS_EXECUTED_TODAY"),
        "DELTA_BACKTEST_CANDIDATES": delta(now, old, "BACKTEST_CANDIDATES"),
        "DELTA_WALK_FORWARD": delta(now, old, "WALK_FORWARD_APPROVED"),
        "DELTA_MONTE_CARLO": delta(now, old, "MONTE_CARLO_APPROVED"),
        "DELTA_PROMOTED_EDGES": delta(now, old, "EDGES_PROMOTED_TODAY"),
        "CURRENT_TOP10": now.get("TOP10"),
        "CURRENT_ALLOCATED_EDGES": now.get("ALLOCATED_EDGES"),
        "HEALTH": now.get("HEALTH"),
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN",
        "generated_at": datetime.now(UTC).isoformat()
    }

LATEST.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
