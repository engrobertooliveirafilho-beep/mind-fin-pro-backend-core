import json
from pathlib import Path
from datetime import datetime, UTC

SRC = Path("reports/P1604_CONFLUENCE_POSITION_EXECUTION_SIMULATOR/p1604_position_management_simulation_report.json")
OUT = Path("reports/P1604_CONFLUENCE_POSITION_EXECUTION_SIMULATOR/p1604b_position_policy_v2.json")

data = json.loads(SRC.read_text(encoding="utf-8"))
summary = data.get("SUMMARY_BY_EDGE", {})

policies = []

for edge_id, s in summary.items():
    asset = s["asset"]
    tf = s["timeframe"]
    avg_final_R = s["avg_final_R"]
    base_R = s["base_total_R"]
    managed_R = s["managed_total_R"]

    if tf in ["M1","M5","M15","M30"]:
        policy_type = "SCALP_RUNNER_LIGHT_PARTIAL"
        policy = {
            "edge_id": edge_id,
            "asset": asset,
            "timeframe": tf,
            "policy_type": policy_type,
            "initial_lot": 0.01,
            "partial_take_profit": {
                "enabled": True,
                "first_partial_at_R": 1.5,
                "first_partial_close_pct": 25,
                "runner_pct": 75
            },
            "break_even": {
                "enabled": True,
                "move_sl_to_entry_after_R": 1.2
            },
            "trailing": {
                "enabled": True,
                "start_after_R": 2.5,
                "trail_by_ATR_multiple": 2.0
            },
            "position_rebuild": {
                "enabled": True,
                "max_rebuilds_per_signal": 1,
                "rebuild_only_if_confluence_score_above": 90,
                "rebuild_lot_multiplier": 0.35
            },
            "scale_in": {
                "enabled": False
            }
        }
    else:
        policy_type = "SWING_POSITION_RUNNER"
        policy = {
            "edge_id": edge_id,
            "asset": asset,
            "timeframe": tf,
            "policy_type": policy_type,
            "initial_lot": 0.01,
            "partial_take_profit": {
                "enabled": True,
                "first_partial_at_R": 3.0,
                "first_partial_close_pct": 20,
                "runner_pct": 80
            },
            "break_even": {
                "enabled": True,
                "move_sl_to_entry_after_R": 2.0
            },
            "trailing": {
                "enabled": True,
                "start_after_R": 4.0,
                "trail_by_ATR_multiple": 3.0
            },
            "position_rebuild": {
                "enabled": True,
                "max_rebuilds_per_signal": 1,
                "rebuild_only_if_confluence_score_above": 92,
                "rebuild_lot_multiplier": 0.25
            },
            "scale_in": {
                "enabled": True,
                "max_additions": 1,
                "add_only_after_profit_R": 2.0,
                "addition_lot_multiplier": 0.25
            }
        }

    policy.update({
        "previous_base_R": base_R,
        "previous_managed_R": managed_R,
        "previous_management_delta_R": round(managed_R - base_R, 6),
        "reason": "V1_PARTIAL_TOO_EARLY_REDUCED_HIGH_PAYOFF",
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

    policies.append(policy)

report = {
    "STATUS": "P1604B_POSITION_POLICY_V2_CREATED",
    "POLICIES": policies,
    "NEXT": "RERUN_P1604_SIMULATOR_WITH_POLICY_V2",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({
    "STATUS": report["STATUS"],
    "POLICIES_CREATED": len(policies),
    "NEXT": report["NEXT"]
}, indent=2))
