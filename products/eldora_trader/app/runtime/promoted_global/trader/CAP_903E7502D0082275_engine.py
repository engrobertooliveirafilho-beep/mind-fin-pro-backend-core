import json, hashlib, csv
from pathlib import Path
from datetime import datetime, UTC

WATCH_DIRS=["data/incoming/mt5","data/incoming/profit","data/incoming/generic_ohlcv","data/incoming/tick"]
REQUIRED_COLUMNS={"time","open","high","low","close"}

def file_hash(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def inspect_file(path):
    p=Path(path)
    with open(p,newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        columns={c.strip().lower() for c in (reader.fieldnames or [])}
        rows=sum(1 for _ in reader)
    missing=sorted(REQUIRED_COLUMNS-columns)
    return {
        "path":str(p),
        "sha256":file_hash(p),
        "rows":rows,
        "columns":sorted(columns),
        "schema_ok":len(missing)==0,
        "missing_columns":missing,
        "status":"READY_FOR_CERTIFICATION" if rows>=200 and not missing else "PENDING_OR_REJECTED",
        "ingested_at":datetime.now(UTC).isoformat()
    }

def scan_watch_dirs():
    found=[]
    for d in WATCH_DIRS:
        Path(d).mkdir(parents=True,exist_ok=True)
        for p in Path(d).glob("*.csv"):
            found.append(inspect_file(p))
    return found

def run():
    out=Path("reports/P13.3_INCREMENTAL_INGESTION")
    out.mkdir(parents=True,exist_ok=True)
    files=scan_watch_dirs()
    manifest={
        "STATUS":"P13.3_INCREMENTAL_INGESTION_IMPLEMENTED",
        "FILES_FOUND":len(files),
        "READY_FOR_CERTIFICATION":sum(x["status"]=="READY_FOR_CERTIFICATION" for x in files),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"ingestion_scan.json").write_text(json.dumps(files,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P13.3_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
