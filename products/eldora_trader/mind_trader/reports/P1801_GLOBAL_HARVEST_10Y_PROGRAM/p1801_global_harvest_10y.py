import json
from pathlib import Path
from datetime import datetime, UTC

SRC = Path("reports/P1800_GLOBAL_MARKET_ABSORPTION_PROGRAM/global_research_jobs.json")
OUT = Path("reports/P1801_GLOBAL_HARVEST_10Y_PROGRAM")
QUEUE_DIR = Path("data/harvest_queue")

jobs = json.loads(SRC.read_text(encoding="utf-8"))

priority_assets = ["XAUUSD","USDJPY","GBPUSD","EURUSD","USDCAD","BTCUSD","NAS100"]
priority_timeframes = ["M5","M15","M30","H1","H4","D1"]

harvest_queue = []
backtest_queue = []

for j in jobs:
    asset = j["asset"]
    tf = j["timeframe"]

    priority = 1
    if asset in priority_assets and tf in priority_timeframes:
        priority = 5
    elif asset in priority_assets:
        priority = 4
    elif tf in ["H1","H4","D1"]:
        priority = 3
    elif tf in ["M15","M30"]:
        priority = 2

    history_years = 10 if tf in ["H4","D1"] else 5
    if tf in ["M1","M5"]:
        history_years = 2

    harvest_queue.append({
        "asset": asset,
        "market": j["market"],
        "timeframe": tf,
        "history_years_target": history_years,
        "priority": priority,
        "source_preference": ["MT5", "NELOGICA", "PROFIT", "CSV_IMPORT"],
        "status": "PENDING_HARVEST",
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

    backtest_queue.append({
        **j,
        "history_years_required": history_years,
        "priority": priority,
        "certification_targets": {
            "RESEARCH": ">=6_MONTHS",
            "CANDIDATE": ">=2_YEARS",
            "INSTITUTIONAL": ">=5_YEARS",
            "ELITE": ">=10_YEARS"
        },
        "status": "WAITING_DATA"
    })

harvest_queue = sorted(harvest_queue, key=lambda x: x["priority"], reverse=True)
backtest_queue = sorted(backtest_queue, key=lambda x: x["priority"], reverse=True)

summary = {
    "STATUS": "P1801_GLOBAL_HARVEST_QUEUE_AND_10Y_DATA_PROGRAM_COMPLETED",
    "HARVEST_ITEMS": len(harvest_queue),
    "BACKTEST_ITEMS": len(backtest_queue),
    "PRIORITY_ASSETS": priority_assets,
    "PRIORITY_TIMEFRAMES": priority_timeframes,
    "P1_TO_P5_PRIORITY_COUNTS": {
        str(p): len([x for x in harvest_queue if x["priority"] == p]) for p in range(1,6)
    },
    "NEXT": "P1802_DATA_AVAILABILITY_AUDIT_AND_MISSING_HISTORY_REPORT",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(QUEUE_DIR/"global_harvest_queue.json").write_text(json.dumps(harvest_queue, indent=2, ensure_ascii=False), encoding="utf-8")
(QUEUE_DIR/"global_backtest_queue.json").write_text(json.dumps(backtest_queue, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT/"p1801_global_harvest_10y_report.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(summary, indent=2, ensure_ascii=False))
