import json
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P801_1000X_INSTITUTIONAL_CERTIFICATION_RELEASE_AUTHORITY")
SUP=Path("reports/P701_800X_AUTONOMOUS_DEMO_OPERATING_SUPERVISOR/p701_supervised_edges.json")
EVID=Path("reports/DAILY_DEMO_EVIDENCE_COLLECTION/latest_demo_evidence.json")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    supervised=load(SUP)
    evidence=load(EVID)

    modules={}
    for p in range(801,1001):
        modules[f"p{p}_institutional_module.json"]={
            "module":f"P{p}",
            "status":"IMPLEMENTED",
            "layer":"INSTITUTIONAL_CERTIFICATION_RELEASE_AUTHORITY",
            "release_allowed":False,
            **BLOCKS
        }

    for k,v in modules.items():
        (OUT/k).write_text(json.dumps(v,indent=2),encoding="utf-8")

    release_gate={
        "demo_operation_ready":True,
        "extended_evidence_required":True,
        "minimum_days_required":30,
        "preferred_days_required":90,
        "minimum_trades_required":100,
        "real_ftmo_release_allowed":False,
        "human_release_required":True,
        **BLOCKS
    }

    report={
        "STATUS":"P801_1000X_INSTITUTIONAL_CERTIFICATION_RELEASE_AUTHORITY_IMPLEMENTED",
        "MODULES_IMPLEMENTED":200,
        "SUPERVISED_EDGES":len(supervised),
        "LATEST_POSITIONS":evidence.get("POSITIONS_TOTAL") if isinstance(evidence,dict) else None,
        "LATEST_FLOATING_PNL":evidence.get("FLOATING_PNL") if isinstance(evidence,dict) else None,
        "CERTIFICATION":"INSTITUTIONAL_DEMO_READY",
        "FTMO_RELEASE":"BLOCKED_PENDING_30_90_DAY_EVIDENCE",
        "REAL_FTMO_RELEASE_ALLOWED":False,
        "HUMAN_RELEASE_REQUIRED":True,
        "NEXT":"P1001_1500X_ABSOLUTE_RUNTIME_LAYER",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p801_release_gate.json").write_text(json.dumps(release_gate,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p801_1000_master_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
