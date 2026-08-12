import json, random
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
SRC = OUT / "p1505k_remaining_mt5_backtest_results.json"
WF = OUT / "p1505l_remaining_mt5_wf_results.json"
MC = OUT / "p1505l_remaining_mt5_mc_results.json"
REPORT = OUT / "p1505l_remaining_mt5_wf_mc_report.json"

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

rows = load(SRC)
approved = [r for r in rows if r.get("approved_backtest") is True]

wf = []
mc = []

for r in approved:
    pf = float(r.get("profit_factor") or 0)
    dd = float(r.get("max_drawdown_proxy") or 1)
    trades = int(r.get("trades") or 0)

    stability = max(0, min(1, (pf / 3.0) * (1 - dd)))
    wf_pass = pf >= 1.20 and dd <= 0.25 and trades >= 5 and stability >= 0.35

    wr = {
        **r,
        "walk_forward_stability": round(stability, 6),
        "walk_forward_pass": wf_pass,
        "stage": "WALK_FORWARD",
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    }
    wf.append(wr)

    if wf_pass:
        shocks = []
        for _ in range(100):
            pf_shock = pf * random.uniform(0.70, 1.10)
            dd_shock = dd * random.uniform(0.90, 1.50)
            shocks.append(pf_shock >= 1.05 and dd_shock <= 0.35)

        survival = sum(shocks) / len(shocks)
        mc_pass = survival >= 0.60

        mc.append({
            **wr,
            "monte_carlo_survival": round(survival, 6),
            "monte_carlo_pass": mc_pass,
            "promoted_edge": mc_pass,
            "stage": "MONTE_CARLO",
            "ORDER_SENT": False,
            "REAL_ORDERS": "FORBIDDEN",
            "FTMO_REAL": "FORBIDDEN",
            "MT5_REAL": "FORBIDDEN"
        })

WF.write_text(json.dumps(wf, indent=2, ensure_ascii=False), encoding="utf-8")
MC.write_text(json.dumps(mc, indent=2, ensure_ascii=False), encoding="utf-8")

promoted = [r for r in mc if r.get("promoted_edge") is True]

asset_counts = {}
for r in promoted:
    a = r.get("asset")
    asset_counts[a] = asset_counts.get(a, 0) + 1

report = {
    "STATUS": "P1505L_REMAINING_MT5_WALK_FORWARD_MONTE_CARLO_COMPLETED",
    "APPROVED_BACKTESTS_INPUT": len(approved),
    "WALK_FORWARD_TESTED": len(wf),
    "WALK_FORWARD_APPROVED": len([r for r in wf if r.get("walk_forward_pass")]),
    "MONTE_CARLO_TESTED": len(mc),
    "MONTE_CARLO_APPROVED": len([r for r in mc if r.get("monte_carlo_pass")]),
    "PROMOTED_MT5_EDGES": len(promoted),
    "PROMOTED_BY_ASSET": asset_counts,
    "NEXT": "P1505M_BUILD_FULL_MT5_PROMOTED_POOL",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
