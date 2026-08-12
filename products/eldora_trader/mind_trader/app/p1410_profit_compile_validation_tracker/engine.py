import json, csv
from pathlib import Path
from datetime import datetime, UTC

WATCH_DIR=Path("data/incoming/profit_compile_results")
REQUIRED_COLUMNS={"strategy_id","file","compiled","error"}

def inspect_compile_file(path):
    p=Path(path)
    with open(p,newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        cols={c.strip().lower() for c in (reader.fieldnames or [])}
        rows=list(reader)
    missing=sorted(REQUIRED_COLUMNS-cols)
    valid=not missing
    compiled=sum(str(r.get("compiled","")).lower() in ("true","1","yes","sim") for r in rows)
    failed=len(rows)-compiled
    return {"file":str(p),"rows":len(rows),"valid":valid,"missing":missing,"compiled":compiled,"failed":failed}

def scan():
    WATCH_DIR.mkdir(parents=True,exist_ok=True)
    return [inspect_compile_file(p) for p in WATCH_DIR.glob("*.csv")]

def run():
    out=Path("reports/P14.10_PROFIT_COMPILE_VALIDATION_TRACKER")
    out.mkdir(parents=True,exist_ok=True)
    results=scan()
    manifest={
        "STATUS":"P14.10_PROFIT_COMPILE_VALIDATION_TRACKER_IMPLEMENTED",
        "FILES_FOUND":len(results),
        "COMPILED_TOTAL":sum(x["compiled"] for x in results),
        "FAILED_TOTAL":sum(x["failed"] for x in results),
        "WATCH_DIR":str(WATCH_DIR),
        "REQUIRED_COLUMNS":sorted(REQUIRED_COLUMNS),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"compile_validation_results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P14.10_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
