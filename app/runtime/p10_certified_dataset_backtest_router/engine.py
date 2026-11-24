import json
from pathlib import Path
from datetime import datetime, timezone
from ..p10_real_dataset_registry_bridge.engine import bridge_dataset

def route_to_backtest(dataset_record, genome_batch):
    if not isinstance(genome_batch,dict) or type(genome_batch.get("batch_start")) is not int or type(genome_batch.get("batch_size")) is not int or genome_batch["batch_start"]<0 or genome_batch["batch_size"]<=0:
        raise ValueError("invalid genome batch")
    reg=bridge_dataset(dataset_record)
    allowed=False
    return {
        "route_status":"BLOCKED_DATASET_NOT_CERTIFIED",
        "dataset_id":reg["dataset_id"],
        "genome_batch":genome_batch,
        "backtest_allowed":allowed,
        "queue_submitted":False,
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "promotion_allowed":False,
        "edge":"NOT_PROVEN",
        "causality":"NOT_PROVEN",
        "created_at":datetime.now(timezone.utc).isoformat()
    }

def route_file(path, source, asset, timeframe, genome_batch):
    if not isinstance(genome_batch,dict) or type(genome_batch.get("batch_start")) is not int or type(genome_batch.get("batch_size")) is not int or genome_batch["batch_start"]<0 or genome_batch["batch_size"]<=0:
        raise ValueError("invalid genome batch")
    from ..p10_real_dataset_registry_bridge.engine import bridge_file
    reg=bridge_file(path, source, asset, timeframe)
    return {
        "route_status":"BLOCKED_PROVENANCE_PENDING" if reg["certification"]["quality_verified"] else "BLOCKED_QUALITY_REJECTED",
        "dataset_id":reg["dataset_id"],
        "file_sha256":reg["file_sha256"],
        "genome_batch":dict(genome_batch),
        "registry":reg,
        "backtest_allowed":False,
        "queue_submitted":False,
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "promotion_allowed":False,
        "edge":"NOT_PROVEN",
        "causality":"NOT_PROVEN",
        "created_at":datetime.now(timezone.utc).isoformat()
    }

def run():
    out=Path("reports/P10.4_CERTIFIED_DATASET_BACKTEST_ROUTER")
    out.mkdir(parents=True,exist_ok=True)
    sample={"dataset_id":"WIN_M1_SAMPLE","asset":"WIN","timeframe":"M1","source":"MT5_CSV","audit":{"schema_ok":True,"rows":220,"timestamp_order":True,"duplicate_ratio":0,"missing_ratio":0,"ohlcv_consistency":True,"unique_closes":60,"volume_validity":True}}
    route=route_to_backtest(sample,{"batch_start":0,"batch_size":1000})
    manifest={
        "STATUS":"P10.4_CERTIFIED_DATASET_BACKTEST_ROUTER_IMPLEMENTED",
        "SAMPLE_EVIDENCE_TYPE":"SYNTHETIC",
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
