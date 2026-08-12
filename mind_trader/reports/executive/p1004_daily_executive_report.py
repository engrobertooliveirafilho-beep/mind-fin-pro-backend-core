import json
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/executive")
EVID=Path("reports/DAILY_DEMO_EVIDENCE_COLLECTION/latest_demo_evidence.json")
P601=Path("reports/P601_700X_INSTITUTIONAL_ALLOCATION_AND_CAPITAL_ENGINE/p601_700_master_report.json")
P801=Path("reports/P801_1000X_INSTITUTIONAL_CERTIFICATION_RELEASE_AUTHORITY/p801_1000_master_report.json")
HEALTH=Path("reports/P1002_RUNTIME_HEALTH_MONITOR/p1002_health_report.json")
REC=Path("reports/P1003_AUTOMATIC_RECOVERY_ENGINE/p1003_recovery_report.json")
BLOCKS={"REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    evid=load(EVID); p601=load(P601); p801=load(P801); health=load(HEALTH); rec=load(REC)
    report={
        "STATUS":"P1004_DAILY_EXECUTIVE_REPORT_COMPLETED",
        "EQUITY":evid.get("EQUITY"),
        "FLOATING_PNL":evid.get("FLOATING_PNL"),
        "POSITIONS_TOTAL":evid.get("POSITIONS_TOTAL"),
        "ALLOCATED_EDGES":p601.get("ALLOCATED_EDGES"),
        "TOTAL_ALLOCATED_RISK_PCT":p601.get("TOTAL_ALLOCATED_RISK_PCT"),
        "SUPERVISED_EDGES":p801.get("SUPERVISED_EDGES"),
        "CERTIFICATION":p801.get("CERTIFICATION"),
        "FTMO_RELEASE":p801.get("FTMO_RELEASE"),
        "HEALTH":health.get("HEALTH"),
        "RECOVERY_REQUIRED":rec.get("RECOVERY_REQUIRED"),
        "MODE":"AUTONOMOUS_EVIDENCE_COLLECTION",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"latest_executive_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": run()
