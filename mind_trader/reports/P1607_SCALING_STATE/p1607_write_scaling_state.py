import json
from pathlib import Path
from datetime import datetime, UTC

SRC = Path("reports/P1606_CONFLUENCE_GATE_AND_SCALING_DECISION_MONITOR/p1606_scaling_decision_monitor.json")
OUT = Path("reports/P1607_SCALING_STATE")
STATE = OUT / "current_scaling_state.json"
HISTORY = OUT / "scaling_history.json"
REPORT = OUT / "p1607_scaling_state_report.json"

data = json.loads(SRC.read_text(encoding="utf-8"))
decisions = data.get("DECISION_TABLE", [])

try:
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
except Exception:
    history = []

state = {
    "STATUS": "P1607_SCALING_STATE_ACTIVE",
    "SCALING_MODE": "DEMO_RESEARCH_ONLY",
    "ACTIVE_EDGES": [],
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "updated_at": datetime.now(UTC).isoformat()
}

for d in decisions:
    state["ACTIVE_EDGES"].append({
        "edge_id": d["edge_id"],
        "asset": d["asset"],
        "timeframe": d["timeframe"],
        "current_lot": d["next_lot"],
        "previous_lot": d["current_lot"],
        "last_decision": d["decision"],
        "confluence_score": d["confluence_score"],
        "avg_managed_R": d["avg_managed_R"],
        "delta_R": d["delta_R"],
        "runtime_health": d["runtime_health"],
        "next_review_hours": 48,
        "can_scale_next_review": True,
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

history.append({
    "timestamp": datetime.now(UTC).isoformat(),
    "decisions": decisions
})

STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
HISTORY.write_text(json.dumps(history[-100:], indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1607_WRITE_SCALING_STATE_COMPLETED",
    "ACTIVE_EDGES": len(state["ACTIVE_EDGES"]),
    "SCALED_TO_0_02": len([e for e in state["ACTIVE_EDGES"] if e["current_lot"] == 0.02]),
    "STATE_FILE": str(STATE),
    "NEXT": "ADD_P1606_P1607_TO_DAILY_ORCHESTRATOR",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
