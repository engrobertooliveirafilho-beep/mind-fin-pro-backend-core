import json
from pathlib import Path
from datetime import datetime, UTC

DETAIL = Path("reports/P1805_SYMBOL_DISCOVERY_AND_10Y_NORMALIZATION/p1805_normalized_10y_detail.json")
OUT = Path("reports/P1806_10Y_BACKTEST_UNLOCK")
REPORT = OUT / "p1806_10y_backtest_unlock_report.json"

datasets = json.loads(DETAIL.read_text(encoding="utf-8"))

strategy_families = [
    "EMA_CROSS",
    "SMA_CROSS",
    "RSI_REVERSION",
    "BOLLINGER_REVERSION",
    "DONCHIAN_BREAKOUT",
    "ATR_TREND",
    "MACD_TREND",
    "FIBO_RETRACE",
    "VWAP_REVERSION",
    "LIQUIDITY_SWEEP_TRIGGER"
]

queue = []

for d in datasets:
    if not d.get("meets_10y"):
        continue

    asset = d["asset"]
    tf = d["timeframe"]

    for family in strategy_families:
        queue.append({
            "asset": asset,
            "timeframe": tf,
            "dataset": d["file"],
            "history_years": d["history_years"],
            "rows": d["rows"],
            "strategy_family": family,
            "certification_target": "ELITE_10Y",
            "mode": "RESEARCH_BACKTEST_ONLY",
            "status": "READY_FOR_10Y_BACKTEST",
            "ORDER_SENT": False,
            "REAL_ORDERS": "FORBIDDEN",
            "FTMO_REAL": "FORBIDDEN",
            "MT5_REAL": "FORBIDDEN"
        })

report = {
    "STATUS": "P1806_10Y_BACKTEST_UNLOCK_COMPLETED",
    "CERTIFIED_10Y_DATASETS": len([d for d in datasets if d.get("meets_10y")]),
    "BACKTEST_JOBS_UNLOCKED": len(queue),
    "ASSETS": sorted(list(set(d["asset"] for d in datasets if d.get("meets_10y")))),
    "TIMEFRAMES": sorted(list(set(d["timeframe"] for d in datasets if d.get("meets_10y")))),
    "NEXT": "P1807_EXECUTE_10Y_PRIORITY_BACKTEST_BATCH",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT / "p1806_10y_backtest_queue.json").write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))
