import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
NORM = Path("data/normalized")
QUEUE = OUT / "p1505e_auto_backtest_queue.json"
REPORT = OUT / "p1505e_auto_backtest_queue_report.json"

STRATEGY_FAMILIES = [
    "SMA_CROSS",
    "EMA_CROSS",
    "RSI_REVERSION",
    "BREAKOUT",
    "DONCHIAN",
    "ATR_TREND",
    "BOLLINGER_REVERSION"
]

PARAM_SETS = {
    "SMA_CROSS": [[5,20],[9,21],[13,55]],
    "EMA_CROSS": [[8,21],[12,26],[21,55]],
    "RSI_REVERSION": [[14,30,70],[10,25,75]],
    "BREAKOUT": [[20],[55]],
    "DONCHIAN": [[20],[50]],
    "ATR_TREND": [[14,2],[21,3]],
    "BOLLINGER_REVERSION": [[20,2],[30,2]]
}

def sig(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()[:24]

def parse_dataset(path):
    name = path.stem.replace("_normalized","")
    parts = name.split("_")
    if name.startswith("MT5_") and len(parts) >= 3:
        return parts[1], parts[2], "MT5"
    tf = parts[-1] if parts[-1] in ["M1","M2","M5","M15","M20","M30","H1","H4","D1","W1","MN1"] else "UNKNOWN"
    asset = "_".join(parts[:-1]) if tf != "UNKNOWN" else name
    return asset, tf, "LOCAL"

datasets = list(NORM.glob("*.csv"))

queue = []
for ds in datasets:
    asset, tf, source = parse_dataset(ds)

    if asset.startswith("TEST_"):
        continue

    priority = "HIGH" if source == "MT5" else "NORMAL"

    for fam in STRATEGY_FAMILIES:
        for params in PARAM_SETS[fam]:
            job = {
                "job_id": sig([str(ds), fam, params]),
                "dataset": str(ds),
                "asset": asset,
                "timeframe": tf,
                "source": source,
                "family": fam,
                "params": params,
                "priority": priority,
                "status": "QUEUED",
                "created_at": datetime.now(UTC).isoformat(),
                "REAL_ORDERS": "FORBIDDEN",
                "FTMO_REAL": "FORBIDDEN",
                "MT5_REAL": "FORBIDDEN"
            }
            queue.append(job)

mt5_jobs = [j for j in queue if j["source"] == "MT5"]
local_jobs = [j for j in queue if j["source"] == "LOCAL"]

report = {
    "STATUS": "P1505E_AUTO_BACKTEST_QUEUE_CREATED",
    "NORMALIZED_DATASETS": len(datasets),
    "QUEUE_JOBS_TOTAL": len(queue),
    "MT5_QUEUE_JOBS": len(mt5_jobs),
    "LOCAL_QUEUE_JOBS": len(local_jobs),
    "STRATEGY_FAMILIES": len(STRATEGY_FAMILIES),
    "NEXT": "P1505F_EXECUTE_MT5_PRIORITY_BACKTEST_BATCH",
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

QUEUE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))
