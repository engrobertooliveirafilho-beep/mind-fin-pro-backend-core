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
    rows=load_json(DATASETS)
    out=[]
    for r in rows:
        ds=r.get("dataset",{})
        if ds.get("certified"):
            name=r.get("normalized","")
            parts=name.replace("_normalized.csv","").split("_")
            symbol=parts[0] if parts else ""
            tf=parts[1] if len(parts)>1 else ""
            out.append({"dataset":name,"symbol":symbol,"timeframe":tf})
    return out

def build_queue():
    arsenal=load_json(ARSENAL)
    datasets=certified_datasets()
    queue=[]
    for a in arsenal:
        asset=a.get("asset")
        for d in datasets:
            if d["symbol"]!=asset:
                continue
            if d["timeframe"] not in PRIORITY_TIMEFRAMES:
                continue
            priority=100
            if asset in ["WINFUT","WDOFUT"]: priority+=50
            if d["timeframe"] in ["M15","M30","H1"]: priority+=20
            if a.get("family") in ["trend_following","breakout","mean_reversion"]: priority+=10
            queue.append({
                "queue_id":f'{asset}_{d["timeframe"]}_{a.get("family")}_{a.get("pattern")}',
                "asset":asset,
                "timeframe":d["timeframe"],
                "dataset":d["dataset"],
                "family":a.get("family"),
                "pattern":a.get("pattern"),
                "status":"QUEUED_FOR_RESEARCH_BACKTEST",
                "priority":priority,
                "live":"FORBIDDEN",
                "real_orders":"FORBIDDEN"
            })
    queue.sort(key=lambda x:x["priority"], reverse=True)
    return queue

def run():
    out=Path("reports/P15.15_WEB_RESEARCH_TO_BACKTEST_QUEUE")
    out.mkdir(parents=True,exist_ok=True)
    q=build_queue()
    manifest={
        "STATUS":"P15.15_WEB_RESEARCH_TO_BACKTEST_QUEUE_IMPLEMENTED",
        "QUEUE_ITEMS":len(q),
        "PRIORITY_ASSETS":PRIORITY_ASSETS,
        "PRIORITY_TIMEFRAMES":PRIORITY_TIMEFRAMES,
        "TOP_20":q[:20],
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN_FOR_QUEUE",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"P15.16_MULTI_FAMILY_BACKTEST_EXECUTOR",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"backtest_queue.json").write_text(json.dumps(q,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P15.15_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
