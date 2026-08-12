import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

def dataset_id(symbol,timeframe,source_hash):
    raw=f"{symbol}|{timeframe}|{source_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

def register_dataset(symbol,timeframe,source_hash,rows,quality_passed,path="mind_trader/reports/P8.61_data_catalog.json"):
    ds={
        "dataset_id":dataset_id(symbol,timeframe,source_hash),
        "symbol":symbol,
        "timeframe":timeframe,
        "source_hash":source_hash,
        "rows":rows,
        "quality_passed":quality_passed,
        "registered_at":datetime.now(UTC).isoformat(),
        "status":"APPROVED_FOR_RESEARCH" if quality_passed and rows>=90 else "BLOCKED_DATASET",
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    catalog=[]
    if p.exists():
        catalog=json.loads(p.read_text(encoding="utf-8"))
    catalog=[x for x in catalog if x["dataset_id"]!=ds["dataset_id"]]+[ds]
    p.write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding="utf-8")
    return ds

def load_catalog(path="mind_trader/reports/P8.61_data_catalog.json"):
    p=Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def require_dataset_approved(dataset_id_value,path="mind_trader/reports/P8.61_data_catalog.json"):
    for ds in load_catalog(path):
        if ds["dataset_id"]==dataset_id_value:
            return {"allowed":ds["status"]=="APPROVED_FOR_RESEARCH","dataset":ds,"decision":"DATASET_OK" if ds["status"]=="APPROVED_FOR_RESEARCH" else "BLOCK_DATASET_NOT_APPROVED","production":"BLOCKED"}
    return {"allowed":False,"decision":"BLOCK_DATASET_NOT_FOUND","production":"BLOCKED"}
