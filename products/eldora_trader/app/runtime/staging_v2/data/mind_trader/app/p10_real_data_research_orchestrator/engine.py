import json
from pathlib import Path
from datetime import datetime, UTC
from app.p10_certified_dataset_backtest_router.engine import route_to_backtest

def orchestrate(records, genome_batches):
    routes=[]
    for ds in records:
        for batch in genome_batches:
            routes.append(route_to_backtest(ds,batch))
    accepted=[r for r in routes if r["backtest_allowed"]]
    blocked=[r for r in routes if not r["backtest_allowed"]]
    return {
        "status":"ORCHESTRATED_RESEARCH_ONLY",
        "routes_total":len(routes),
        "routes_accepted":len(accepted),
        "routes_blocked":len(blocked),
        "routes":routes,
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "promotion_allowed":False,
        "edge":"NOT_PROVEN",
        "causality":"NOT_PROVEN",
        "created_at":datetime.now(UTC).isoformat()
    }

def run():
    out=Path("reports/P10.5_REAL_DATA_RESEARCH_ORCHESTRATOR")
    out.mkdir(parents=True,exist_ok=True)
    good={"dataset_id":"WIN_M1_SAMPLE","asset":"WIN","timeframe":"M1","source":"MT5_CSV","audit":{"schema_ok":True,"rows":220,"timestamp_order":True,"duplicate_ratio":0,"missing_ratio":0,"ohlcv_consistency":True,"unique_closes":60,"volume_validity":True}}
    bad={"dataset_id":"BAD_SAMPLE","asset":"WIN","timeframe":"M1","source":"MT5_CSV","audit":{"schema_ok":False,"rows":10}}
    batches=[{"batch_start":0,"batch_size":1000},{"batch_start":1000,"batch_size":1000}]
    orchestration=orchestrate([good,bad],batches)
    manifest={
        "STATUS":"P10.5_REAL_DATA_RESEARCH_ORCHESTRATOR_IMPLEMENTED",
        "ROUTES_TOTAL":orchestration["routes_total"],
        "ROUTES_ACCEPTED":orchestration["routes_accepted"],
        "ROUTES_BLOCKED":orchestration["routes_blocked"],
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "PROMOTION_ALLOWED":False,
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True
    }
    (out/"P10.5_orchestration.json").write_text(json.dumps(orchestration,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P10.5_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
