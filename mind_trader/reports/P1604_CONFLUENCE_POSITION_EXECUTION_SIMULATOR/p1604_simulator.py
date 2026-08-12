import json
from pathlib import Path
from datetime import datetime, UTC

POLICY = Path("reports/P1603_POSITION_MANAGEMENT_ENGINE/p1603_position_management_policy.json")
TRADES = Path("reports/P1505_DATA_INGESTION_ENGINE/p1505n_trade_level_trades.json")
OUT = Path("reports/P1604_CONFLUENCE_POSITION_EXECUTION_SIMULATOR")
REPORT = OUT / "p1604_position_management_simulation_report.json"

OUT.mkdir(parents=True, exist_ok=True)

def load(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

policy_report = load(POLICY, {})
policies = policy_report.get("POLICIES", [])
trades = load(TRADES, [])

def simulate_trade(t):
    pnl = float(t.get("pnl_pct") or 0)
    mae = abs(float(t.get("mae_pct") or 0.0001))
    risk = max(mae, 0.0001)
    r = pnl / risk

    base_result = r

    if r >= 2:
        managed = (0.50 * 1.0) + (0.25 * 2.0) + (0.25 * r)
    elif r >= 1:
        managed = (0.50 * 1.0) + (0.50 * max(r, 0))
    elif r > 0:
        managed = r
    else:
        managed = max(r, -1)

    rebuild_bonus = 0
    if managed >= 1:
        rebuild_bonus = managed * 0.25

    scale_in_bonus = 0
    if managed >= 2:
        scale_in_bonus = managed * 0.25

    final_r = managed + rebuild_bonus + scale_in_bonus

    return {
        **t,
        "base_R": round(base_result, 6),
        "managed_R": round(managed, 6),
        "rebuild_bonus_R": round(rebuild_bonus, 6),
        "scale_in_bonus_R": round(scale_in_bonus, 6),
        "final_R": round(final_r, 6)
    }

simulated = []
summary = {}

for p in policies:
    edge_id = p["edge_id"]
    edge_trades = [t for t in trades if t.get("edge_id") == edge_id]

    sims = [simulate_trade(t) for t in edge_trades]
    simulated.extend(sims)

    total = len(sims)
    wins = [x for x in sims if x["final_R"] > 0]
    losses = [x for x in sims if x["final_R"] <= 0]

    base_sum = sum(x["base_R"] for x in sims)
    final_sum = sum(x["final_R"] for x in sims)

    summary[edge_id] = {
        "asset": p["asset"],
        "timeframe": p["timeframe"],
        "family": p["family"],
        "trades": total,
        "base_total_R": round(base_sum, 6),
        "managed_total_R": round(final_sum, 6),
        "improvement_R": round(final_sum - base_sum, 6),
        "win_rate_managed": round(len(wins) / total, 6) if total else 0,
        "avg_final_R": round(final_sum / total, 6) if total else 0,
        "position_policy": p
    }

(OUT / "p1604_simulated_trade_management.json").write_text(json.dumps(simulated, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1604_CONFLUENCE_POSITION_EXECUTION_SIMULATOR_COMPLETED",
    "POLICIES_INPUT": len(policies),
    "TRADES_SIMULATED": len(simulated),
    "SUMMARY_BY_EDGE": summary,
    "NEXT": "P1605_ADAPTIVE_POSITION_SIZING_ENGINE",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({
    "STATUS": report["STATUS"],
    "POLICIES_INPUT": report["POLICIES_INPUT"],
    "TRADES_SIMULATED": report["TRADES_SIMULATED"],
    "NEXT": report["NEXT"]
}, indent=2, ensure_ascii=False))
