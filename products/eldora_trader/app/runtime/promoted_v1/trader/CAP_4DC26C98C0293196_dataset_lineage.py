import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

def lineage_hash(obj):
    raw=json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def create_dataset_lineage(dataset, connector_manifest, path="mind_trader/reports/P8.64_dataset_lineage.json"):
    lineage={
        "lineage":"P8.64_DATASET_LINEAGE",
        "created_at":datetime.now(UTC).isoformat(),
        "dataset_id":dataset.get("dataset_id"),
        "symbol":dataset.get("symbol"),
        "timeframe":dataset.get("timeframe"),
        "source_file":connector_manifest.get("file_path"),
        "source_hash":connector_manifest.get("file_checksum"),
        "db_path":connector_manifest.get("db_path"),
        "catalog_status":dataset.get("status"),
        "quality":connector_manifest.get("ingestion_result",{}).get("quality"),
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }
    lineage["lineage_hash"]=lineage_hash(lineage)
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(lineage,ensure_ascii=False,indent=2),encoding="utf-8")
    return lineage

def verify_lineage(lineage):
    h=lineage.get("lineage_hash")
    x=dict(lineage); x.pop("lineage_hash",None)
    return {
        "valid":lineage_hash(x)==h,
        "dataset_id":lineage.get("dataset_id"),
        "decision":"LINEAGE_OK" if lineage_hash(x)==h else "LINEAGE_TAMPERED",
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }
