import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1603_POSITION_MANAGEMENT_ENGINE")
SRC = Path("reports/P1505_DATA_INGESTION_ENGINE/p1506_ranked_convergence_payoff_edges.json")
REPORT = OUT / "p1603_position_management_policy.json"

def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []

edges = load(SRC)

policies = []

for e in edges[:30]:
    payoff = float(e.get("payoff_ratio_real") or 0)
    wr = float(e.get("win_rate") or 0)
    exp = float(e.get("expectancy_per_trade_real") or 0)
    scalp = bool(e.get("scalp_candidate"))

    if payoff >= 5 and wr >= 0.65 and exp > 0:
        policy = {
            "edge_id": e.get("edge_id"),
            "asset": e.get("asset"),
            "timeframe": e.get("timeframe"),
            "family": e.get("family"),
            "mode": "SIMULATED_POSITION_MANAGEMENT",
            "initial_lot": 0.01,
            "partial_take_profit": {
                "enabled": True,
                "first_partial_at_R": 1.0,
                "first_partial_close_pct": 50,
                "second_partial_at_R": 2.0,
                "second_partial_close_pct": 25,
                "runner_pct": 25
            },
            "break_even": {
                "enabled": True,
                "move_sl_to_entry_after_R": 1.0
            },
            "trailing": {
                "enabled": True,
                "start_after_R": 2.0,
                "trail_by_ATR_multiple": 1.5
            },
            "position_rebuild": {
                "enabled": True,
                "allow_reentry_after_partial": True,
                "max_rebuilds_per_signal": 2,
                "rebuild_only_if_confluence_score_above": 85,
                "rebuild_lot_multiplier": 0.50
            },
            "scale_in": {
                "enabled": True,
                "max_additions": 2,
                "add_only_after_profit_R": 1.0,
                "addition_lot_multiplier": 0.50
            },
            "risk_lock": {
                "max_total_lot_demo": 0.04,
                "max_daily_loss_pct": 1.0,
                "max_edge_loss_streak": 3,
                "on_loss_streak": "FREEZE_EDGE_48H"
            },
            "ORDER_SENT": False,
            "REAL_ORDERS": "FORBIDDEN",
            "FTMO_REAL": "FORBIDDEN",
            "MT5_REAL": "FORBIDDEN"
        }
        policies.append(policy)

report = {
    "STATUS": "P1603_POSITION_MANAGEMENT_ENGINE_COMPLETED",
    "INPUT_EDGES": len(edges),
    "POLICIES_CREATED": len(policies),
    "FEATURES": [
        "PARTIAL_TAKE_PROFIT",
        "BREAK_EVEN",
        "TRAILING_STOP",
        "POSITION_REBUILD",
        "SCALE_IN",
        "RISK_LOCK"
    ],
    "POLICIES": policies,
    "NEXT": "P1604_CONFLUENCE_POSITION_EXECUTION_SIMULATOR",
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
    "NEXT": report["NEXT"],
    "REAL_ORDERS": "FORBIDDEN"
}, indent=2, ensure_ascii=False))
