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
    schema_ok=not missing
    schema_sample_sufficient=len(rows)>=200
    return {
        "path":str(p),
        "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
        "rows":len(rows),
        "columns":sorted(cols),
        "schema_ok":schema_ok,
        "schema_sample_sufficient":schema_sample_sufficient,
        "missing":missing,
        "certified":False,
        "provenance_verified":False,
        "chronology_verified":False,
        "canonical_manifest_reconciled":False,
        "source":"UNVERIFIED"
    }

def certify_all():
    files=list(Path(DATA_DIR).glob("MT5_*.csv"))
    return [inspect_csv(f) for f in files]

def run():
    out=Path("reports/P13.10_MT5_NORMALIZED_DATASET_CERTIFICATION")
    out.mkdir(parents=True,exist_ok=True)
    results=certify_all()
    manifest={
        "STATUS":"UNVERIFIED_PENDING_PROVENANCE_RECONCILIATION",
        "FILES_TOTAL":len(results),
        "FILES_CERTIFIED":0,
        "FILES_REJECTED":len(results),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":False,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"certified_mt5_datasets.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P13.10_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
