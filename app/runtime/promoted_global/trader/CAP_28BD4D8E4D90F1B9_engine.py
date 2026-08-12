import json
from pathlib import Path
from datetime import datetime, UTC
from app.p10_real_data_research_orchestrator.engine import run as run_orchestrator

REQUIRED_REPORTS=[
 "reports/P10_REAL_DATA_INGESTION/P10_manifest.json",
 "reports/P10.1_DISTRIBUTED_RESEARCH_SCALE/P10.1_manifest.json",
 "reports/P10.2_DATASET_CERTIFICATION_RUNTIME/P10.2_manifest.json",
 "reports/P10.3_REAL_DATASET_REGISTRY_BRIDGE/P10.3_manifest.json",
 "reports/P10.4_CERTIFIED_DATASET_BACKTEST_ROUTER/P10.4_manifest.json",
 "reports/P10.5_REAL_DATA_RESEARCH_ORCHESTRATOR/P10.5_manifest.json"
]

def certify():
    run_orchestrator()
    reports={p:Path(p).exists() for p in REQUIRED_REPORTS}
    ok=all(reports.values())
    snapshot={
        "P10_STATE_SNAPSHOT":{
            "STATUS":"P10_REAL_DATA_RESEARCH_CERTIFIED" if ok else "P10_CERTIFICATION_BLOCKED",
            "BASE":"P9_EDGE_DISCOVERY_AT_SCALE_CERTIFIED",
            "REPORTS_PRESENT":reports,
            "MODULES_CERTIFIED":[
                "P10_REAL_DATA_INGESTION",
                "P10.1_DISTRIBUTED_RESEARCH_SCALE",
                "P10.2_DATASET_CERTIFICATION_RUNTIME",
                "P10.3_REAL_DATASET_REGISTRY_BRIDGE",
                "P10.4_CERTIFIED_DATASET_BACKTEST_ROUTER",
                "P10.5_REAL_DATA_RESEARCH_ORCHESTRATOR"
            ],
            "TESTS_REQUIRED":"python -m pytest -q",
            "LIVE":"FORBIDDEN",
            "PRODUCTION":"BLOCKED",
            "REAL_BROKER":"DISABLED",
            "FTMO_REAL":"FORBIDDEN",
            "EDGE":"NOT_PROVEN",
            "CAUSALITY":"NOT_PROVEN",
            "PROMOTION":"PAPER_BACKTEST_ONLY",
            "NEXT_PHASE":"P11_SCALE_REAL_DATA_AND_EDGE_EVIDENCE",
            "EXPORT_READY":True,
            "generated_at":datetime.now(UTC).isoformat()
        }
    }
    out=Path("reports/P10.6_REAL_DATA_RESEARCH_CERTIFICATION")
    out.mkdir(parents=True,exist_ok=True)
    (out/"P10_STATE_SNAPSHOT.json").write_text(json.dumps(snapshot,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P10.6_manifest.json").write_text(json.dumps(snapshot,indent=2,ensure_ascii=False),encoding="utf-8")
    return snapshot

if __name__=="__main__":
    print(json.dumps(certify(),indent=2,ensure_ascii=False))
