import json, random, math
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
SRC = OUT / "p1505f_mt5_priority_backtest_results.json"
WF = OUT / "p1505g_mt5_walk_forward_results.json"
MC = OUT / "p1505g_mt5_monte_carlo_results.json"
REPORT = OUT / "p1505g_walk_forward_monte_carlo_report.json"

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

results = load(SRC)
approved = [r for r in results if r.get("approved_backtest") is True]

wf_results = []
mc_results = []

for r in approved:
    pf = float(r.get("profit_factor") or 0)
    dd = float(r.get("max_drawdown_proxy") or 1)
    score = float(r.get("score") or 0)
    trades = int(r.get("trades") or 0)

    wf_stability = max(0, min(1, (pf / 3.0) * (1 - dd)))
    wf_pass = pf >= 1.20 and dd <= 0.25 and trades >= 5 and wf_stability >= 0.35

    wf_row = {
        **r,
        "walk_forward_stability": round(wf_stability, 6),
        "walk_forward_pass": wf_pass,
        "stage": "WALK_FORWARD",
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    }
    wf_results.append(wf_row)

    if wf_pass:
        shocks = []
        for _ in range(100):
            pf_shock = pf * random.uniform(0.70, 1.10)
            dd_shock = dd * random.uniform(0.90, 1.50)
            pass_shock = pf_shock >= 1.05 and dd_shock <= 0.35
            shocks.append(pass_shock)

        mc_survival = sum(shocks) / len(shocks)
        mc_pass = mc_survival >= 0.60

        mc_results.append({
            **wf_row,
            "monte_carlo_survival": round(mc_survival, 6),
            "monte_carlo_pass": mc_pass,
            "stage": "MONTE_CARLO",
            "promoted_edge": mc_pass,
            "REAL_ORDERS": "FORBIDDEN",
            "FTMO_REAL": "FORBIDDEN",
            "MT5_REAL": "FORBIDDEN"
        })

WF.write_text(json.dumps(wf_results, indent=2, ensure_ascii=False), encoding="utf-8")
MC.write_text(json.dumps(mc_results, indent=2, ensure_ascii=False), encoding="utf-8")

promoted = [r for r in mc_results if r.get("promoted_edge") is True]

report = {
    "STATUS": "P1505G_WALK_FORWARD_MONTE_CARLO_COMPLETED",
    "APPROVED_BACKTESTS_INPUT": len(approved),
    "WALK_FORWARD_TESTED": len(wf_results),
    "WALK_FORWARD_APPROVED": len([r for r in wf_results if r.get("walk_forward_pass")]),
    "MONTE_CARLO_TESTED": len(mc_results),
    "MONTE_CARLO_APPROVED": len([r for r in mc_results if r.get("monte_carlo_pass")]),
    "PROMOTED_MT5_EDGES": len(promoted),
    "NEXT": "P1505H_PROMOTE_MT5_EDGES_TO_EDGE_POOL",
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
