import json
from pathlib import Path
from datetime import datetime, UTC

HIST = Path("reports/P1608_MIN_5Y_BACKTEST_HISTORY_GATE/p1608_dataset_history_detail.json")
EDGES = Path("reports/P1505_DATA_INGESTION_ENGINE/p1506_ranked_convergence_payoff_edges.json")
OUT = Path("reports/P1608_MIN_5Y_BACKTEST_HISTORY_GATE")
REPORT = OUT / "p1608b_profile_report_scalp_day_swing.json"

def load(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

history = load(HIST, [])
edges = load(EDGES, [])

def profile(tf):
    if tf in ["M1","M5"]:
        return "SCALP"
    if tf in ["M15","M30","H1"]:
        return "DAY_TRADE"
    if tf in ["H4","D1","W1","MN1"]:
        return "SWING_TRADE"
    return "UNKNOWN"

history_key = {}
for h in history:
    if "asset" in h and "timeframe" in h:
        history_key[(h["asset"], h["timeframe"])] = h

profiles = {
    "SCALP": [],
    "DAY_TRADE": [],
    "SWING_TRADE": [],
    "UNKNOWN": []
}

for e in edges:
    asset = e.get("asset")
    tf = e.get("timeframe")
    p = profile(tf)

    h = history_key.get((asset, tf), {})
    row = {
        "edge_id": e.get("edge_id"),
        "asset": asset,
        "timeframe": tf,
        "family": e.get("family"),
        "params": e.get("params"),
        "trades": e.get("trades"),
        "win_rate": e.get("win_rate"),
        "payoff_ratio_real": e.get("payoff_ratio_real"),
        "expectancy_per_trade_real": e.get("expectancy_per_trade_real"),
        "profit_factor_real": e.get("profit_factor_real"),
        "avg_holding_bars": e.get("avg_holding_bars"),
        "deployment_score": e.get("deployment_score"),
        "scalp_candidate": e.get("scalp_candidate"),
        "history_years": h.get("history_years"),
        "min_5y_pass": h.get("min_5y_pass", False),
        "certification": "INSTITUTIONAL_5Y" if h.get("min_5y_pass") else "RESEARCH_ONLY_LT_5Y",
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    }
    profiles[p].append(row)

summary = {}

for p, rows in profiles.items():
    rows_sorted = sorted(
        rows,
        key=lambda x: (
            bool(x.get("min_5y_pass")),
            float(x.get("deployment_score") or 0),
            float(x.get("payoff_ratio_real") or 0),
            float(x.get("expectancy_per_trade_real") or 0)
        ),
        reverse=True
    )
    profiles[p] = rows_sorted

    summary[p] = {
        "edges": len(rows_sorted),
        "institutional_5y_edges": len([x for x in rows_sorted if x["min_5y_pass"]]),
        "research_only_edges": len([x for x in rows_sorted if not x["min_5y_pass"]]),
        "best_edge": rows_sorted[0] if rows_sorted else None,
        "top10": rows_sorted[:10]
    }

report = {
    "STATUS": "P1608B_PROFILE_REPORT_SCALP_DAY_SWING_COMPLETED",
    "PROFILE_RULES": {
        "SCALP": ["M1","M5"],
        "DAY_TRADE": ["M15","M30","H1"],
        "SWING_TRADE": ["H4","D1","W1","MN1"]
    },
    "SUMMARY": summary,
    "NEXT": "P1609_REHARVEST_5Y_MT5_HISTORY_AND_REBACKTEST_BY_PROFILE",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({
    "STATUS": report["STATUS"],
    "SCALP_EDGES": summary["SCALP"]["edges"],
    "DAY_TRADE_EDGES": summary["DAY_TRADE"]["edges"],
    "SWING_TRADE_EDGES": summary["SWING_TRADE"]["edges"],
    "SCALP_5Y": summary["SCALP"]["institutional_5y_edges"],
    "DAY_TRADE_5Y": summary["DAY_TRADE"]["institutional_5y_edges"],
    "SWING_TRADE_5Y": summary["SWING_TRADE"]["institutional_5y_edges"],
    "NEXT": report["NEXT"]
}, indent=2, ensure_ascii=False))
