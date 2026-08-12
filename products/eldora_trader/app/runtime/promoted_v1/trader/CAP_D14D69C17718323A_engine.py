import json, hashlib, csv
from pathlib import Path
from datetime import datetime, UTC

SUPPORTED_SOURCES=["MT5_CSV","PROFIT_CSV","GENERIC_OHLCV_CSV","TICK_CSV"]
REQUIRED_COLUMNS={"time","open","high","low","close"}

def file_hash(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def inspect_csv(path):
    path=Path(path)
    with open(path,newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        cols={c.strip().lower() for c in (reader.fieldnames or [])}
        rows=list(reader)
    missing=sorted(REQUIRED_COLUMNS-cols)
    return {
        "path":str(path),
        "sha256":file_hash(path),
        "rows":len(rows),
        "columns":sorted(cols),
        "missing_required_columns":missing,
        "schema_ok":not missing,
        "certified":len(rows)>=200 and not missing
    }

def register_file(path, source, asset, timeframe):
    if source not in SUPPORTED_SOURCES:
        raise ValueError(f"unsupported source: {source}")
    audit=inspect_csv(path)
    dataset_id=hashlib.sha256(f"{asset}:{timeframe}:{source}:{audit['sha256']}".encode()).hexdigest()[:18]
    return {
        "dataset_id":dataset_id,
        "source":source,
        "asset":asset,
        "timeframe":timeframe,
        "audit":audit,
        "live":"FORBIDDEN",
        "real_broker":"DISABLED",
        "edge":"NOT_PROVEN",
        "causality":"NOT_PROVEN",
        "created_at":datetime.now(UTC).isoformat()
    }

def run_demo():
    out=Path("reports/P10_REAL_DATA_INGESTION")
    out.mkdir(parents=True,exist_ok=True)
    manifest={
        "STATUS":"P10_REAL_DATA_INGESTION_ENGINE_IMPLEMENTED",
        "SUPPORTED_SOURCES":SUPPORTED_SOURCES,
        "REQUIRED_COLUMNS":sorted(REQUIRED_COLUMNS),
        "CERTIFICATION_RULE":"rows>=200 and schema_ok",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True
    }
    (out/"P10_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run_demo(),indent=2,ensure_ascii=False))
