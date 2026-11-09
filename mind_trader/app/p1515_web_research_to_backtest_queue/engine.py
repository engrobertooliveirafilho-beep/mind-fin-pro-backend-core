import json
from pathlib import Path
from datetime import datetime,UTC

ARSENAL=Path("reports/P15.13_P15.14_WEB_STRATEGY_ARSENAL/asset_strategy_arsenal.json")
DATASETS=Path("reports/P15.3_P15.5_PROFIT_MARKET_DATA_PIPELINE/dataset_results.json")

PRIORITY_ASSETS=["WINFUT","WDOFUT","IBOV","PETR4","VALE3","IFIX","CSAN3"]
PRIORITY_TIMEFRAMES=["M15","M20","M30","H1","D1"]

def load_json(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def certified_datasets():
    # No canonical manifest verification is available here: reject self-asserted flags.
    # A separate hash-verified provenance gate must be implemented before promotion.
    return []

def build_queue():
    return []

def run():
    out=Path("reports/P15.15_WEB_RESEARCH_TO_BACKTEST_QUEUE")
    out.mkdir(parents=True,exist_ok=True)
    q=build_queue()
    manifest={
        "STATUS":"BLOCKED_PENDING_CANONICAL_DATASET_RECONCILIATION",
        "QUEUE_ITEMS":len(q),
        "PRIORITY_ASSETS":PRIORITY_ASSETS,
        "PRIORITY_TIMEFRAMES":PRIORITY_TIMEFRAMES,
        "TOP_20":[],
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN_FOR_QUEUE",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"RECONCILE_ORIGINAL_DATASET_MANIFESTS_BEFORE_BACKTEST",
        "EXPORT_READY":False,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"backtest_queue.json").write_text(json.dumps(q,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P15.15_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
