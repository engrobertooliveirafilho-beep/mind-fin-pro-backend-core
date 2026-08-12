import json, hashlib
from pathlib import Path
from datetime import datetime, UTC
from app.p10_dataset_certification_runtime.engine import register_certification

def bridge_dataset(dataset_record):
    dataset_id=dataset_record.get("dataset_id") or hashlib.sha256(json.dumps(dataset_record,sort_keys=True).encode()).hexdigest()[:18]
    cert=register_certification(dataset_id,dataset_record.get("audit",{}))
    return {
        "dataset_id":dataset_id,
        "asset":dataset_record.get("asset"),
        "timeframe":dataset_record.get("timeframe"),
        "source":dataset_record.get("source"),
        "registry_status":"REGISTERED_CERTIFIED" if cert["certification"]["certified"] else "REGISTERED_REJECTED_OR_PENDING",
        "certification":cert,
        "backtest_allowed":cert["certification"]["certified"],
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "promotion_allowed":False,
        "registered_at":datetime.now(UTC).isoformat()
    }

def bridge_many(records):
    return [bridge_dataset(r) for r in records]

def run():
    out=Path("reports/P10.3_REAL_DATASET_REGISTRY_BRIDGE")
    out.mkdir(parents=True,exist_ok=True)
    sample={
        "dataset_id":"WIN_M1_SAMPLE",
        "asset":"WIN",
        "timeframe":"M1",
        "source":"MT5_CSV",
        "audit":{"schema_ok":True,"rows":220,"timestamp_order":True,"duplicate_ratio":0,"missing_ratio":0,"ohlcv_consistency":True,"unique_closes":60,"volume_validity":True}
    }
    registry=bridge_many([sample])
    manifest={
        "STATUS":"P10.3_REAL_DATASET_REGISTRY_BRIDGE_IMPLEMENTED",
        "REGISTERED":len(registry),
        "CERTIFIED":sum(1 for r in registry if r["backtest_allowed"]),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True
    }
    (out/"P10.3_registry.json").write_text(json.dumps(registry,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P10.3_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
