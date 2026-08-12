import json
from pathlib import Path
from datetime import datetime, UTC
from app.p13_data_source_registry.engine import build_registry

WATCH_DIRS=[
    "data/incoming/mt5",
    "data/incoming/profit",
    "data/incoming/generic_ohlcv",
    "data/incoming/tick"
]

def build_acquisition_plan():
    registry=build_registry()
    plan=[]
    for row in registry:
        plan.append({
            "registry_id":row["registry_id"],
            "source_id":row["source_id"],
            "asset":row["asset"],
            "timeframe":row["timeframe"],
            "watch_dir":f"data/incoming/{row['source_id'].lower()}",
            "expected_format":"CSV",
            "status":"WAITING_FOR_FILE",
            "auto_ingest_enabled":True,
            "certification_required":True,
            "cloud_sync_required":True,
            "live":"FORBIDDEN",
            "real_broker":"DISABLED"
        })
    return plan

def run():
    out=Path("reports/P13.2_DATA_ACQUISITION_AUTOMATION")
    out.mkdir(parents=True,exist_ok=True)
    for d in WATCH_DIRS:
        Path(d).mkdir(parents=True,exist_ok=True)
    plan=build_acquisition_plan()
    manifest={
        "STATUS":"P13.2_DATA_ACQUISITION_AUTOMATION_IMPLEMENTED",
        "WATCH_DIRS":WATCH_DIRS,
        "ACQUISITION_SLOTS":len(plan),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"DROP_REAL_CSV_FILES_IN_WATCH_DIRS",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"acquisition_plan.json").write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P13.2_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
