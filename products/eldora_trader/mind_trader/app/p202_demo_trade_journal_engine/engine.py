import json
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P202_DEMO_TRADE_JOURNAL_ENGINE")
EVIDENCE=Path("reports/DAILY_DEMO_EVIDENCE_COLLECTION/latest_demo_evidence.json")
ANALYSIS=Path("reports/P201_DAILY_DEMO_EVIDENCE_ANALYZER/p201_report.json")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    ev=load(EVIDENCE)
    an=load(ANALYSIS)
    positions=ev.get("POSITIONS",[])

    journal=[]
    for p in positions:
        journal.append({
            "ticket":p.get("ticket"),
            "symbol":p.get("symbol"),
            "type":p.get("type"),
            "volume":p.get("volume"),
            "price_open":p.get("price_open"),
            "price_current":p.get("price_current"),
            "sl":p.get("sl"),
            "tp":p.get("tp"),
            "profit":p.get("profit"),
            "swap":p.get("swap"),
            "comment":p.get("comment"),
            "risk_state":an.get("RISK_STATE"),
            "recommendation":an.get("RECOMMENDATION"),
            "journal_status":"OPEN_POSITION_RECORDED",
            **BLOCKS,
            "journaled_at":datetime.now(UTC).isoformat()
        })

    report={
        "STATUS":"P202_DEMO_TRADE_JOURNAL_ENGINE_IMPLEMENTED",
        "POSITIONS_JOURNALED":len(journal),
        "RISK_STATE":an.get("RISK_STATE"),
        "RECOMMENDATION":an.get("RECOMMENDATION"),
        "NEW_ORDER_SENT":False,
        "POSITION_CLOSE_SENT":False,
        "NEXT":"P203_DEMO_TRADE_OUTCOME_TRACKER",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p202_trade_journal.json").write_text(json.dumps(journal,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p202_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
