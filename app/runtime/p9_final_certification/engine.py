import json, datetime
from pathlib import Path
from ..p9_research_command_center.engine import build_dashboard

REQUIRED_REPORTS=[
 "reports/P9.1_DATA_EXPANSION_ENGINE/P9.1_STATE_SNAPSHOT.json",
 "reports/P9.2_GENOME_EXPLOSION_ENGINE/P9.2_manifest.json",
 "reports/P9.3_MASSIVE_BACKTEST_GRID/P9.3_manifest.json",
 "reports/P9.4_DNA_EXTRACTION_ENGINE/P9.4_manifest.json",
 "reports/P9.5_EDGE_DISCOVERY_FACTORY/P9.5_manifest.json",
 "reports/P9.6_CONTINUOUS_RESEARCH_RUNTIME/P9.6_manifest.json",
 "reports/P9.7_RESEARCH_COMMAND_CENTER/P9.7_manifest.json"
]

def certify():
    dashboard=build_dashboard()
    reports={p:Path(p).exists() for p in REQUIRED_REPORTS}
    passed=False  # Report presence is not execution evidence.
    cert={
        "P9_STATE_SNAPSHOT":{
            "STATUS":"P9_EDGE_DISCOVERY_AT_SCALE_CERTIFIED" if passed else "P9_CERTIFICATION_BLOCKED",
            "BASE":"P8.100_PAPER_RESEARCH_V1_CERTIFIED",
            "TESTS_REQUIRED":"run pytest -q",
            "REPORTS_PRESENT":reports,
            "MODULES_CERTIFIED":[],
            "CERTIFICATION_REASON":"VERIFIED_EXECUTION_EVIDENCE_REQUIRED",
            "TESTS_EXECUTED":False,
            "LIVE":"FORBIDDEN",
            "PRODUCTION":"BLOCKED",
            "REAL_BROKER":"DISABLED",
            "FTMO_REAL":"FORBIDDEN",
            "EDGE":"NOT_PROVEN",
            "CAUSALITY":"NOT_PROVEN",
            "PROMOTION":"BLOCKED",
            "NEXT_PHASE":"BLOCKED_PENDING_CERTIFICATION",
            "EXPORT_READY":True,
            "generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    }
    out=Path("reports/P9.100_FINAL_CERTIFICATION")
    out.mkdir(parents=True,exist_ok=True)
    (out/"P9_STATE_SNAPSHOT.json").write_text(json.dumps(cert,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P9.100_final_certification.json").write_text(json.dumps(cert,indent=2,ensure_ascii=False),encoding="utf-8")
    return cert

if __name__=="__main__":
    print(json.dumps(certify(),indent=2,ensure_ascii=False))

