import json
from pathlib import Path
from datetime import datetime, UTC

SRC = Path("reports/P1604_CONFLUENCE_POSITION_EXECUTION_SIMULATOR/p1604e_policy_v3_simulation_report.json")
OUT = Path("reports/P1605_ADAPTIVE_POSITION_SIZING_ENGINE")
REPORT = OUT / "p1605_adaptive_position_sizing_policy.json"

OUT.mkdir(parents=True, exist_ok=True)

data = json.loads(SRC.read_text(encoding="utf-8"))
summary = data.get("SUMMARY_BY_EDGE", {})

policies = []

for edge_id, s in summary.items():
    avg_r = float(s.get("avg_managed_R_v3") or 0)
    delta_r = float(s.get("delta_R_v3") or 0)
    trades = int(s.get("trades") or 0)

    if avg_r >= 1.0 and delta_r > 0 and trades >= 5:
        status = "ELIGIBLE_TO_SCALE"
    else:
        status = "HOLD_001"

    policies.append({
        "edge_id": edge_id,
        "asset": s["asset"],
        "timeframe": s["timeframe"],
        "policy_type": s["policy_type"],
        "current_lot": 0.01,
        "next_lot_if_approved": 0.02,
        "evaluation_window_hours": 48,
        "scaling_status": status,
        "scaling_rules": {
            "start_lot": 0.01,
            "double_lot_every_hours": 48,
            "double_only_if": {
                "avg_managed_R": ">= 1.0",
                "delta_R": "> 0",
                "min_trades": ">= 5",
                "max_drawdown_pct": "<= 3",
                "loss_streak": "< 3",
                "confluence_score": ">= 85"
            },
            "reduce_50pct_if": {
                "max_drawdown_pct": "> 3",
                "loss_streak": ">= 3",
                "avg_managed_R": "<= 0"
            },
            "reset_to_001_if": {
                "max_drawdown_pct": "> 5",
                "daily_loss_pct": "> 2",
                "runtime_health": "!= GREEN"
            }
        },
        "caps": {
            "max_lot_demo": 0.16,
            "max_lot_ftmo_sim": 0.04,
            "max_total_open_lot_demo": 0.20,
            "max_edges_scaled_same_time": 3
        },
        "performance_snapshot": {
            "trades": trades,
            "base_total_R": s["base_total_R"],
            "managed_total_R_v3": s["managed_total_R_v3"],
            "delta_R_v3": s["delta_R_v3"],
            "avg_managed_R_v3": s["avg_managed_R_v3"]
        },
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

report = {
    "STATUS": "P1605_ADAPTIVE_POSITION_SIZING_ENGINE_COMPLETED",
    "POLICIES_CREATED": len(policies),
    "INITIAL_LOT": 0.01,
    "SCALING_MODEL": "DOUBLE_EVERY_48H_IF_PERFORMANCE_APPROVED",
    "ELIGIBLE_TO_SCALE": len([p for p in policies if p["scaling_status"] == "ELIGIBLE_TO_SCALE"]),
    "POLICIES": policies,
    "NEXT": "P1606_CONFLUENCE_GATE_AND_SCALING_DECISION_MONITOR",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({
    "STATUS": report["STATUS"],
    "POLICIES_CREATED": report["POLICIES_CREATED"],
    "ELIGIBLE_TO_SCALE": report["ELIGIBLE_TO_SCALE"],
    "NEXT": report["NEXT"],
    "REAL_ORDERS": "FORBIDDEN"
}, indent=2))
