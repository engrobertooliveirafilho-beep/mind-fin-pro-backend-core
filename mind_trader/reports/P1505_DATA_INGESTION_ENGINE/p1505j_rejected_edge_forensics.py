import json
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
BT = OUT / "p1505f_mt5_priority_backtest_results.json"
SEL = OUT / "p1505i_diversified_mt5_edge_selection.json"
REPORT = OUT / "p1505j_rejected_edge_forensics_report.json"

def load(p):
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

backtests = load(BT)
selected = load(SEL)

selected_keys = set(
    f"{e.get('asset')}|{e.get('timeframe')}|{e.get('family')}|{json.dumps(e.get('params'), sort_keys=True, default=str)}"
    for e in selected
)

asset_stats = defaultdict(lambda: {
    "tested": 0,
    "approved_backtest": 0,
    "selected": 0,
    "avg_pf": 0,
    "avg_dd": 0,
    "avg_score": 0,
    "families": defaultdict(int),
    "timeframes": defaultdict(int),
    "failure_reasons": defaultdict(int)
})

rejected_rows = []

for r in backtests:
    asset = r.get("asset")
    tf = r.get("timeframe")
    fam = r.get("family")
    key = f"{asset}|{tf}|{fam}|{json.dumps(r.get('params'), sort_keys=True, default=str)}"

    pf = float(r.get("profit_factor") or 0)
    dd = float(r.get("max_drawdown_proxy") or 0)
    score = float(r.get("score") or 0)
    trades = int(r.get("trades") or 0)
    approved = bool(r.get("approved_backtest"))

    s = asset_stats[asset]
    s["tested"] += 1
    s["avg_pf"] += pf
    s["avg_dd"] += dd
    s["avg_score"] += score
    s["families"][fam] += 1
    s["timeframes"][tf] += 1

    if approved:
        s["approved_backtest"] += 1

    if key in selected_keys:
        s["selected"] += 1
        continue

    reasons = []
    if trades < 5:
        reasons.append("LOW_TRADES")
    if pf < 1.20:
        reasons.append("LOW_PF")
    if dd > 0.25:
        reasons.append("HIGH_DD")
    if approved and key not in selected_keys:
        reasons.append("DIVERSIFICATION_CAP_OR_RANKING")
    if not reasons:
        reasons.append("UNKNOWN_OR_RANKING")

    for reason in reasons:
        s["failure_reasons"][reason] += 1

    rejected_rows.append({
        "asset": asset,
        "timeframe": tf,
        "family": fam,
        "params": r.get("params"),
        "trades": trades,
        "profit_factor": pf,
        "max_drawdown_proxy": dd,
        "score": score,
        "approved_backtest": approved,
        "rejection_reasons": reasons
    })

asset_report = []
for asset, s in asset_stats.items():
    tested = max(1, s["tested"])
    asset_report.append({
        "asset": asset,
        "tested": s["tested"],
        "approved_backtest": s["approved_backtest"],
        "selected": s["selected"],
        "approval_rate": round(s["approved_backtest"] / tested, 4),
        "selection_rate": round(s["selected"] / tested, 4),
        "avg_pf": round(s["avg_pf"] / tested, 6),
        "avg_dd": round(s["avg_dd"] / tested, 6),
        "avg_score": round(s["avg_score"] / tested, 6),
        "families_tested": dict(s["families"]),
        "timeframes_tested": dict(s["timeframes"]),
        "failure_reasons": dict(s["failure_reasons"])
    })

asset_report = sorted(asset_report, key=lambda x: (x["selected"], x["approved_backtest"], x["avg_score"]), reverse=True)

zero_selected = [a for a in asset_report if a["selected"] == 0]

summary = {
    "STATUS": "P1505J_REJECTED_EDGE_FORENSICS_COMPLETED",
    "BACKTEST_ROWS_INPUT": len(backtests),
    "SELECTED_EDGES_INPUT": len(selected),
    "REJECTED_OR_NOT_SELECTED": len(rejected_rows),
    "ASSETS_ANALYZED": len(asset_report),
    "ZERO_SELECTED_ASSETS": zero_selected,
    "ASSET_FORENSICS": asset_report,
    "NEXT": "P1505K_ADAPTIVE_STRATEGY_EXPANSION_FOR_ZERO_SELECTED_ASSETS",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "p1505j_rejected_edges_detail.json").write_text(json.dumps(rejected_rows, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "STATUS": summary["STATUS"],
    "BACKTEST_ROWS_INPUT": summary["BACKTEST_ROWS_INPUT"],
    "SELECTED_EDGES_INPUT": summary["SELECTED_EDGES_INPUT"],
    "REJECTED_OR_NOT_SELECTED": summary["REJECTED_OR_NOT_SELECTED"],
    "ASSETS_ANALYZED": summary["ASSETS_ANALYZED"],
    "ZERO_SELECTED_ASSETS": [a["asset"] for a in zero_selected],
    "NEXT": summary["NEXT"],
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN"
}, indent=2, ensure_ascii=False))
