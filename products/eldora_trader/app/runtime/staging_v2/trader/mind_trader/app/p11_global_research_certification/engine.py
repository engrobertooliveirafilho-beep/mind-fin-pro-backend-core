import json
from pathlib import Path
from datetime import datetime, UTC
from app.p11_edge_evidence_at_scale.engine import run as run_scale

REQUIRED_REPORTS=[
 "reports/P11.3_GLOBAL_MARKET_REGISTRY/P11.3_manifest.json",
 "reports/P11.4_DATA_COVERAGE_ENGINE/P11.4_manifest.json",
 "reports/P11.5_MULTI_MARKET_RESEARCH_GRID/P11.5_manifest.json",
 "reports/P11.6_EDGE_EVIDENCE_AT_SCALE/P11.6_manifest.json"
]

def certify():
    run_scale()
    reports={p:Path(p).exists() for p in REQUIRED_REPORTS}
    ok=all(reports.values())
    snapshot={
        "P11_STATE_SNAPSHOT":{
            "STATUS":"P11_GLOBAL_RESEARCH_CERTIFIED" if ok else "P11_CERTIFICATION_BLOCKED",
            "BASE":"P10_REAL_DATA_RESEARCH_CERTIFIED",
            "REPORTS_PRESENT":reports,
            "MODULES_CERTIFIED":[
                "P11.3_GLOBAL_MARKET_REGISTRY",
                "P11.4_DATA_COVERAGE_ENGINE",
                "P11.5_MULTI_MARKET_RESEARCH_GRID",
                "P11.6_EDGE_EVIDENCE_AT_SCALE"
            ],
            "LIVE":"FORBIDDEN",
            "PRODUCTION":"BLOCKED",
            "REAL_BROKER":"DISABLED",
            "FTMO_REAL":"FORBIDDEN",
            "EDGE":"NOT_PROVEN",
            "CAUSALITY":"NOT_PROVEN",
            "NEXT_PHASE":"P12_REAL_DATA_LOADING_AND_CLOUD_EXPORT",
            "EXPORT_READY":True,
            "generated_at":datetime.now(UTC).isoformat()
        }
    }
    out=Path("reports/P11.7_GLOBAL_RESEARCH_CERTIFICATION")
    out.mkdir(parents=True,exist_ok=True)
    (out/"P11_STATE_SNAPSHOT.json").write_text(json.dumps(snapshot,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P11.7_manifest.json").write_text(json.dumps(snapshot,indent=2,ensure_ascii=False),encoding="utf-8")
    return snapshot

if __name__=="__main__":
    print(json.dumps(certify(),indent=2,ensure_ascii=False))
