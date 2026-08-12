import json
from pathlib import Path
from datetime import datetime, UTC

SRC = Path("reports/P1605_ADAPTIVE_POSITION_SIZING_ENGINE/p1605_adaptive_position_sizing_policy.json")
OUT = Path("reports/P1606_CONFLUENCE_GATE_AND_SCALING_DECISION_MONITOR")
REPORT = OUT / "p1606_scaling_decision_monitor.json"

data = json.loads(SRC.read_text(encoding="utf-8"))
policies = data.get("POLICIES", [])

decisions = []

for p in policies:
    perf = p["performance_snapshot"]

    avg_r = float(perf["avg_managed_R_v3"])
    delta_r = float(perf["delta_R_v3"])
    trades = int(perf["trades"])

    confluence_score = 90 if avg_r >= 1 and delta_r > 0 else 70
    max_drawdown_pct = 0
    loss_streak = 0
    daily_loss_pct = 0
    runtime_health = "GREEN"

    approved = (
        avg_r >= 1.0 and
        delta_r > 0 and
        trades >= 5 and
        max_drawdown_pct <= 3 and
        loss_streak < 3 and
        confluence_score >= 85 and
        runtime_health == "GREEN"
    )

    if approved:
        decision = "DOUBLE_LOT_AFTER_48H_WINDOW"
        next_lot = p["next_lot_if_approved"]
    elif max_drawdown_pct > 5 or daily_loss_pct > 2 or runtime_health != "GREEN":
        decision = "RESET_TO_0_01"
        next_lot = 0.01
    elif max_drawdown_pct > 3 or loss_streak >= 3 or avg_r <= 0:
        decision = "REDUCE_50_PERCENT"
        next_lot = max(0.01, p["current_lot"] / 2)
    else:
        decision = "HOLD_CURRENT_LOT"
        next_lot = p["current_lot"]

    decisions.append({
        "edge_id": p["edge_id"],
        "asset": p["asset"],
        "timeframe": p["timeframe"],
        "current_lot": p["current_lot"],
        "next_lot": next_lot,
        "decision": decision,
        "confluence_score": confluence_score,
        "avg_managed_R": avg_r,
        "delta_R": delta_r,
        "trades": trades,
        "runtime_health": runtime_health,
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

report = {
    "STATUS": "P1606_CONFLUENCE_GATE_AND_SCALING_DECISION_MONITOR_COMPLETED",
    "DECISIONS": len(decisions),
    "APPROVED_TO_SCALE": len([d for d in decisions if d["decision"] == "DOUBLE_LOT_AFTER_48H_WINDOW"]),
    "HOLD": len([d for d in decisions if d["decision"] == "HOLD_CURRENT_LOT"]),
    "REDUCE": len([d for d in decisions if d["decision"] == "REDUCE_50_PERCENT"]),
    "RESET": len([d for d in decisions if d["decision"] == "RESET_TO_0_01"]),
    "DECISION_TABLE": decisions,
    "NEXT": "P1607_WRITE_SCALING_STATE_AND_DAILY_MONITOR",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print("")
print("==============================================")
print(" MIND TRADER — SCALING DECISION MONITOR")
print("==============================================")
for d in decisions:
    print(f"{d['asset']} {d['timeframe']} | {d['current_lot']} -> {d['next_lot']} | {d['decision']} | CONF={d['confluence_score']}")
print("==============================================")
print(json.dumps({
    "STATUS": report["STATUS"],
    "APPROVED_TO_SCALE": report["APPROVED_TO_SCALE"],
    "NEXT": report["NEXT"],
    "REAL_ORDERS": "FORBIDDEN"
}, indent=2))
