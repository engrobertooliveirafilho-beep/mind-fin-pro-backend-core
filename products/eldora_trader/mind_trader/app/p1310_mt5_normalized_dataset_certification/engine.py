import json, csv, hashlib
from pathlib import Path
from datetime import datetime, UTC

DATA_DIR="data/normalized"

def inspect_csv(path):
    p=Path(path)
    with open(p,newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        cols={c.strip().lower() for c in (reader.fieldnames or [])}
        rows=list(reader)
    required={"time","open","high","low","close"}
    missing=sorted(required-cols)
    return {
        "path":str(p),
        "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
        "rows":len(rows),
        "columns":sorted(cols),
        "schema_ok":not missing,
        "missing":missing,
        "certified":len(rows)>=200 and not missing,
        "source":"MT5" if p.name.upper().startswith("MT5_") else "UNKNOWN"
    }

def certify_all():
    files=list(Path(DATA_DIR).glob("MT5_*.csv"))
    return [inspect_csv(f) for f in files]

def run():
    out=Path("reports/P13.10_MT5_NORMALIZED_DATASET_CERTIFICATION")
    out.mkdir(parents=True,exist_ok=True)
    results=certify_all()
    manifest={
        "STATUS":"P13.10_MT5_NORMALIZED_DATASET_CERTIFICATION_IMPLEMENTED",
        "FILES_TOTAL":len(results),
        "FILES_CERTIFIED":sum(x["certified"] for x in results),
        "FILES_REJECTED":sum(not x["certified"] for x in results),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"certified_mt5_datasets.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P13.10_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
