import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

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
        "min_rows":type(rows) is int and rows>=200,
        "timestamp_order":audit.get("timestamp_order",False) is True,
        "duplicate_ratio":type(audit.get("duplicate_ratio")) in (int,float) and 0<=audit["duplicate_ratio"]<=0.001,
        "missing_ratio":type(audit.get("missing_ratio")) in (int,float) and 0<=audit["missing_ratio"]<=0.001,
        "ohlcv_consistency":audit.get("ohlcv_consistency",False) is True,
        "price_variance":type(audit.get("unique_closes")) is int and audit["unique_closes"]>=20,
        "volume_validity":audit.get("volume_validity",False) is True
    }
    score=sum(checks.values())/len(checks)
    return {
        "checks":checks,
        "certification_score":round(score,6),
        "certified":False,
        "reported_checks_pass":score==1.0,
        "status":"BLOCKED_PENDING_VERIFIED_FILE_AUDIT",
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "edge":"NOT_PROVEN",
        "causality":"NOT_PROVEN",
        "certified_at":datetime.now(timezone.utc).isoformat()
    }

def audit_file(path, source, asset, timeframe):
    from ..p10_real_data_ingestion.engine import register_file
    record = register_file(path, source, asset, timeframe)
    audit = record["audit"]
    result = register_certification(record["dataset_id"], audit)
    result["file_sha256"] = audit["sha256"]
    result["file_audit_executed"] = audit.get("validation_executed") is True
    result["quality_verified"] = (
        result["file_audit_executed"]
        and audit.get("quality_pass") is True
        and result["certification"]["reported_checks_pass"] is True
    )
    result["provenance_verified"] = False
    result["certification"]["status"] = (
        "QUALITY_VERIFIED_PROVENANCE_PENDING" if result["quality_verified"]
        else "QUALITY_REJECTED"
    )
    return result

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
        "SAMPLE_EVIDENCE_TYPE":"SYNTHETIC",
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
