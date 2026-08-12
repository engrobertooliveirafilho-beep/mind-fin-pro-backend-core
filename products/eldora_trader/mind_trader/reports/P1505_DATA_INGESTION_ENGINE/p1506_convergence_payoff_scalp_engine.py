import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
SRC = OUT / "p1505n_edge_trade_metrics.json"
REPORT = OUT / "p1506_convergence_payoff_scalp_report.json"
RANKED = OUT / "p1506_ranked_convergence_payoff_edges.json"

def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []

rows = load(SRC)

ranked = []
for e in rows:
    trades = int(e.get("trades") or 0)
    payoff = float(e.get("payoff_ratio_real") or 0)
    exp = float(e.get("expectancy_per_trade_real") or 0)
    pf = float(e.get("profit_factor_real") or 0)
    wr = float(e.get("win_rate") or 0)
    duration = float(e.get("avg_holding_bars") or 0)
    tf = e.get("timeframe")

    if trades < 5 or payoff <= 1 or exp <= 0 or pf <= 1:
        continue

    scalp_bonus = 0
    if tf in ["M1","M5","M15","M30"] and duration <= 5:
        scalp_bonus = 1.25

    convergence = 0
    convergence += 1 if payoff >= 2 else 0
    convergence += 1 if exp > 0 else 0
    convergence += 1 if pf >= 1.5 else 0
    convergence += 1 if wr >= 0.5 else 0
    convergence += 1 if trades >= 10 else 0
    convergence += 1 if scalp_bonus > 0 else 0

    deployment_score = (
        payoff * 2.0 +
        pf * 1.5 +
        exp * 100 +
        wr * 2.0 +
        convergence * 1.25 +
        scalp_bonus
    )

    edge = {
        **e,
        "convergence_points": convergence,
        "scalp_candidate": scalp_bonus > 0,
        "payoff_priority": payoff,
        "deployment_score": round(deployment_score, 6),
        "selection_mode": "MAX_CONVERGENCE_MAX_PAYOFF",
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    }
    ranked.append(edge)

ranked = sorted(
    ranked,
    key=lambda x: (
        x["deployment_score"],
        x["payoff_ratio_real"],
        x["expectancy_per_trade_real"],
        x["profit_factor_real"]
    ),
    reverse=True
)

best_by_asset = {}
for e in ranked:
    a = e["asset"]
    if a not in best_by_asset:
        best_by_asset[a] = e

scalp_edges = [e for e in ranked if e.get("scalp_candidate")]

report = {
    "STATUS": "P1506_CONVERGENCE_PAYOFF_SCALP_ENGINE_COMPLETED",
    "INPUT_EDGES": len(rows),
    "VALID_EDGES": len(ranked),
    "SCALP_CANDIDATES": len(scalp_edges),
    "BEST_EDGE_GLOBAL": ranked[0] if ranked else None,
    "BEST_EDGE_BY_ASSET": best_by_asset,
    "TOP10": ranked[:10],
    "NEXT": "P1600_ADAPTIVE_POSITION_SIZING_ENGINE",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

RANKED.write_text(json.dumps(ranked, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "STATUS": report["STATUS"],
    "VALID_EDGES": report["VALID_EDGES"],
    "SCALP_CANDIDATES": report["SCALP_CANDIDATES"],
    "BEST_EDGE_GLOBAL": report["BEST_EDGE_GLOBAL"],
    "NEXT": report["NEXT"]
}, indent=2, ensure_ascii=False))
