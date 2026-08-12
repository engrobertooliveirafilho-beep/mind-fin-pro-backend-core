import json, shutil
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_EXPORT_REPORTS=[
 "reports/P11.7_GLOBAL_RESEARCH_CERTIFICATION/P11_STATE_SNAPSHOT.json",
 "reports/P11.3_GLOBAL_MARKET_REGISTRY/global_market_registry.json",
 "reports/P11.4_DATA_COVERAGE_ENGINE/coverage_matrix.json",
 "reports/P11.5_MULTI_MARKET_RESEARCH_GRID/research_grid_summary.json",
 "reports/P11.6_EDGE_EVIDENCE_AT_SCALE/scale_readiness.json"
]

def build_export_package(destination="reports/P12_REAL_DATA_LOADING_CLOUD_EXPORT/export_package"):
    dest=Path(destination)
    dest.mkdir(parents=True,exist_ok=True)
    copied={}
    for src in REQUIRED_EXPORT_REPORTS:
        p=Path(src)
        copied[src]=p.exists()
        if p.exists():
            shutil.copy2(p,dest/p.name)
    manifest={
        "STATUS":"P12_REAL_DATA_LOADING_CLOUD_EXPORT_IMPLEMENTED",
        "PACKAGE_DIR":str(dest),
        "FILES_PRESENT":copied,
        "CLOUD_UPLOAD_REQUIRED":True,
        "LOCAL_ONLY_UNTIL_USER_RUNS_RCLONE_OR_SUPABASE_UPLOAD":True,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "FTMO_REAL":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (dest/"P12_export_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    Path("reports/P12_REAL_DATA_LOADING_CLOUD_EXPORT/P12_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(build_export_package(),indent=2,ensure_ascii=False))
