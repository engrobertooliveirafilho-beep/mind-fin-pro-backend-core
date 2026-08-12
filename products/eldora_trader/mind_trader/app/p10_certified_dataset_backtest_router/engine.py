import json
from pathlib import Path
from datetime import datetime, UTC
from app.p10_real_dataset_registry_bridge.engine import bridge_dataset

def route_to_backtest(dataset_record, genome_batch):
    reg=bridge_dataset(dataset_record)
    allowed=reg["backtest_allowed"] is True
    return {
        "route_status":"BACKTEST_QUEUED" if allowed else "BLOCKED_DATASET_NOT_CERTIFIED",
        "dataset_id":reg["dataset_id"],
        "genome_batch":genome_batch,
        "backtest_allowed":allowed,
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "promotion_allowed":False,
        "edge":"NOT_PROVEN",
        "causality":"NOT_PROVEN",
        "created_at":datetime.now(UTC).isoformat()
    }

def run():
    out=Path("reports/P10.4_CERTIFIED_DATASET_BACKTEST_ROUTER")
    out.mkdir(parents=True,exist_ok=True)
    sample={"dataset_id":"WIN_M1_SAMPLE","asset":"WIN","timeframe":"M1","source":"MT5_CSV","audit":{"schema_ok":True,"rows":220,"timestamp_order":True,"duplicate_ratio":0,"missing_ratio":0,"ohlcv_consistency":True,"unique_closes":60,"volume_validity":True}}
    route=route_to_backtest(sample,{"batch_start":0,"batch_size":1000})
    manifest={
        "STATUS":"P10.4_CERTIFIED_DATASET_BACKTEST_ROUTER_IMPLEMENTED",
        "SAMPLE_ROUTE_STATUS":route["route_status"],
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "PROMOTION_ALLOWED":False,
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True
    }
    (out/"P10.4_route_sample.json").write_text(json.dumps(route,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P10.4_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
