import json
from pathlib import Path
from datetime import datetime, UTC

POLICY = Path("reports/P1604_CONFLUENCE_POSITION_EXECUTION_SIMULATOR/p1604b_position_policy_v2.json")
TRADES = Path("reports/P1505_DATA_INGESTION_ENGINE/p1505n_trade_level_trades.json")
OUT = Path("reports/P1604_CONFLUENCE_POSITION_EXECUTION_SIMULATOR")
REPORT = OUT / "p1604c_policy_v2_simulation_report.json"

def load(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

policies = load(POLICY, {}).get("POLICIES", [])
trades = load(TRADES, [])

def simulate(t, p):
    pnl = float(t.get("pnl_pct") or 0)
    risk = max(abs(float(t.get("mae_pct") or 0)), 0.0001)
    r = pnl / risk

    partial = p["partial_take_profit"]
    first_R = partial["first_partial_at_R"]
    close_pct = partial["first_partial_close_pct"] / 100
    runner_pct = partial["runner_pct"] / 100

    if r >= first_R:
        managed = close_pct * first_R + runner_pct * r
    elif r > 0:
        managed = r
    else:
        managed = max(r, -1)

    return {**t, "base_R": round(r,6), "managed_R_v2": round(managed,6)}

summary = {}
all_sims = []

for p in policies:
    edge_id = p["edge_id"]
    edge_trades = [t for t in trades if t.get("edge_id") == edge_id]
    sims = [simulate(t,p) for t in edge_trades]
    all_sims.extend(sims)

    base = sum(x["base_R"] for x in sims)
    managed = sum(x["managed_R_v2"] for x in sims)

    summary[edge_id] = {
        "asset": p["asset"],
        "timeframe": p["timeframe"],
        "policy_type": p["policy_type"],
        "trades": len(sims),
        "base_total_R": round(base,6),
        "managed_total_R_v2": round(managed,6),
        "delta_R_v2": round(managed-base,6),
        "v1_delta_R": p.get("previous_management_delta_R"),
        "improved_vs_v1": round((managed-base) - float(p.get("previous_management_delta_R") or 0),6),
        "avg_managed_R_v2": round(managed/max(len(sims),1),6)
    }

(OUT/"p1604c_policy_v2_simulated_trades.json").write_text(json.dumps(all_sims,indent=2,ensure_ascii=False),encoding="utf-8")

report = {
    "STATUS":"P1604C_POLICY_V2_SIMULATION_COMPLETED",
    "POLICIES_TESTED":len(policies),
    "TRADES_SIMULATED":len(all_sims),
    "SUMMARY_BY_EDGE":summary,
    "NEXT":"P1605_ADAPTIVE_POSITION_SIZING_ENGINE",
    "ORDER_SENT":False,
    "REAL_ORDERS":"FORBIDDEN",
    "FTMO_REAL":"FORBIDDEN",
    "MT5_REAL":"FORBIDDEN",
    "generated_at":datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(report,indent=2,ensure_ascii=False))
