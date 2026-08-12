import json
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P1003_AUTOMATIC_RECOVERY_ENGINE")
REQUIRED=[
"reports/DAILY_DEMO_EVIDENCE_COLLECTION/latest_demo_evidence.json",
"reports/P601_700X_INSTITUTIONAL_ALLOCATION_AND_CAPITAL_ENGINE/p601_700_master_report.json",
"reports/P801_1000X_INSTITUTIONAL_CERTIFICATION_RELEASE_AUTHORITY/p801_1000_master_report.json"
]
BLOCKS={"REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    missing=[p for p in REQUIRED if not Path(p).exists()]
    report={
        "STATUS":"P1003_AUTOMATIC_RECOVERY_ENGINE_COMPLETED",
        "MISSING_ARTIFACTS":missing,
        "RECOVERY_REQUIRED":len(missing)>0,
        "RECOVERY_ACTION":"RERUN_MASTER_ORCHESTRATOR" if missing else "NONE",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1003_recovery_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": run()
