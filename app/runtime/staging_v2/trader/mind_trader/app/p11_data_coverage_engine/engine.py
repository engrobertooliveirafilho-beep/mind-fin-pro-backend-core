import json
from pathlib import Path
from datetime import datetime, UTC
from app.p11_global_market_registry.engine import build_registry

TIMEFRAMES=["TICK","M1","M5","M15","M30","H1","H4","D1"]

def build_coverage_matrix():
    registry=build_registry()
    matrix=[]
    for asset in registry:
        for tf in TIMEFRAMES:
            matrix.append({
                "asset_id":asset["asset_id"],
                "symbol":asset["symbol"],
                "asset_class":asset["asset_class"],
                "country":asset["country"],
                "timeframe":tf,
                "dataset_required":True,
                "dataset_present":False,
                "certified":False,
                "coverage_status":"MISSING_DATA",
                "live":"FORBIDDEN",
                "real_broker":"DISABLED"
            })
    return matrix

def coverage_summary(matrix):
    total=len(matrix)
    present=sum(x["dataset_present"] for x in matrix)
    certified=sum(x["certified"] for x in matrix)
    return {
        "total_slots":total,
        "dataset_present":present,
        "certified":certified,
        "missing":total-present,
        "coverage_ratio":round(present/total,6) if total else 0,
        "certification_ratio":round(certified/total,6) if total else 0
    }

def run():
    out=Path("reports/P11.4_DATA_COVERAGE_ENGINE")
    out.mkdir(parents=True,exist_ok=True)
    matrix=build_coverage_matrix()
    summary=coverage_summary(matrix)
    manifest={
        "STATUS":"P11.4_DATA_COVERAGE_ENGINE_IMPLEMENTED",
        "SUMMARY":summary,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"INGEST_REAL_DATA_TO_IMPROVE_COVERAGE",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"coverage_matrix.json").write_text(json.dumps(matrix,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"coverage_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P11.4_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
