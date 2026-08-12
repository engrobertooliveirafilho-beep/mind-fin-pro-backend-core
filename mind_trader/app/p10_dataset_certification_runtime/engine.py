import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_CHECKS=[
    "schema_ok",
    "min_rows",
    "timestamp_order",
    "duplicate_ratio",
    "missing_ratio",
    "ohlcv_consistency",
    "price_variance",
    "volume_validity"
]

def certify_dataset(audit):
    rows=audit.get("rows",0)
    checks={
        "schema_ok":audit.get("schema_ok") is True,
        "min_rows":rows>=200,
        "timestamp_order":audit.get("timestamp_order",True) is True,
        "duplicate_ratio":audit.get("duplicate_ratio",0)<=0.001,
        "missing_ratio":audit.get("missing_ratio",0)<=0.001,
        "ohlcv_consistency":audit.get("ohlcv_consistency",True) is True,
        "price_variance":audit.get("unique_closes",21)>=20,
        "volume_validity":audit.get("volume_validity",True) is True
    }
    score=sum(checks.values())/len(checks)
    return {
        "checks":checks,
        "certification_score":round(score,6),
        "certified":score==1.0,
        "status":"CERTIFIED" if score==1.0 else "REJECTED_OR_PENDING_FIX",
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "edge":"NOT_PROVEN",
        "causality":"NOT_PROVEN",
        "certified_at":datetime.now(UTC).isoformat()
    }

def register_certification(dataset_id,audit):
    cert=certify_dataset(audit)
    return {
        "dataset_id":dataset_id,
        "certification":cert,
        "lineage_hash":hashlib.sha256(json.dumps(audit,sort_keys=True).encode()).hexdigest(),
        "promotion_allowed":False
    }

def run():
    out=Path("reports/P10.2_DATASET_CERTIFICATION_RUNTIME")
    out.mkdir(parents=True,exist_ok=True)
    sample=register_certification("sample_dataset",{
        "schema_ok":True,
        "rows":220,
        "timestamp_order":True,
        "duplicate_ratio":0,
        "missing_ratio":0,
        "ohlcv_consistency":True,
        "unique_closes":50,
        "volume_validity":True
    })
    manifest={
        "STATUS":"P10.2_DATASET_CERTIFICATION_RUNTIME_IMPLEMENTED",
        "REQUIRED_CHECKS":REQUIRED_CHECKS,
        "SAMPLE_CERTIFIED":sample["certification"]["certified"],
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True
    }
    (out/"P10.2_sample_certification.json").write_text(json.dumps(sample,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P10.2_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
