import json
from pathlib import Path
from datetime import datetime, UTC

SRC = Path("reports/P1604_CONFLUENCE_POSITION_EXECUTION_SIMULATOR/p1604c_policy_v2_simulation_report.json")
OUT = Path("reports/P1604_CONFLUENCE_POSITION_EXECUTION_SIMULATOR/p1604d_policy_v3_no_partial_runner.json")

data = json.loads(SRC.read_text(encoding="utf-8"))
summary = data["SUMMARY_BY_EDGE"]

policies = []

for edge_id, s in summary.items():
    tf = s["timeframe"]
    is_scalp = tf in ["M1","M5","M15","M30"]

    policy = {
        "edge_id": edge_id,
        "asset": s["asset"],
        "timeframe": tf,
        "family": s["family"] if "family" in s else None,
        "policy_type": "NO_PARTIAL_HIGH_PAYOFF_RUNNER",
        "initial_lot": 0.01,
        "partial_take_profit": {
            "enabled": False,
            "reason": "PARTIAL_REDUCED_TOTAL_R_IN_V1_AND_V2"
        },
        "break_even": {
            "enabled": True,
            "move_sl_to_entry_after_R": 2.0 if is_scalp else 3.0
        },
        "trailing": {
            "enabled": True,
            "start_after_R": 3.0 if is_scalp else 5.0,
            "trail_by_ATR_multiple": 2.5 if is_scalp else 3.5
        },
        "position_rebuild": {
            "enabled": True,
            "max_rebuilds_per_signal": 1,
            "rebuild_only_if_confluence_score_above": 92 if is_scalp else 95,
            "rebuild_lot_multiplier": 0.25
        },
        "scale_in": {
            "enabled": True,
            "max_additions": 1,
            "add_only_after_profit_R": 2.0 if is_scalp else 3.0,
            "addition_lot_multiplier": 0.25
        },
        "previous_base_R": s["base_total_R"],
        "previous_v2_managed_R": s["managed_total_R_v2"],
        "previous_v2_delta_R": s["delta_R_v2"],
        "objective": "MAXIMIZE_PAYOFF_WITHOUT_EARLY_PARTIAL",
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    }

    policies.append(policy)

report = {
    "STATUS": "P1604D_POLICY_V3_NO_PARTIAL_RUNNER_CREATED",
    "POLICIES_CREATED": len(policies),
    "POLICIES": policies,
    "NEXT": "SIMULATE_POLICY_V3_AND_BUILD_P1605_ADAPTIVE_POSITION_SIZING",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({
    "STATUS": report["STATUS"],
    "POLICIES_CREATED": report["POLICIES_CREATED"],
    "NEXT": report["NEXT"]
}, indent=2))
