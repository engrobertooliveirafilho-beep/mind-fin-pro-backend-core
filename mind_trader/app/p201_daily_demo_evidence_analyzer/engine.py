import json
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P201_DAILY_DEMO_EVIDENCE_ANALYZER")
SRC=Path("reports/DAILY_DEMO_EVIDENCE_COLLECTION/latest_demo_evidence.json")

BLOCKS={
    "LIVE":"FORBIDDEN",
    "REAL_BROKER":"DISABLED",
    "REAL_ORDERS":"FORBIDDEN",
    "FTMO_REAL":"FORBIDDEN",
    "MT5_REAL":"FORBIDDEN"
}

def run():

    OUT.mkdir(parents=True,exist_ok=True)

    if not SRC.exists():
        report={
            "STATUS":"NO_EVIDENCE_FOUND",
            **BLOCKS
        }
        return report

    data=json.loads(SRC.read_text(encoding="utf-8"))

    pnl=float(data.get("FLOATING_PNL",0))
    equity=float(data.get("EQUITY",0))
    balance=float(data.get("BALANCE",0))

    dd=max(0,(balance-equity))

    risk_state="NORMAL"

    if dd>100:
        risk_state="ATTENTION"

    if dd>500:
        risk_state="DEFENSIVE"

    if dd>1000:
        risk_state="CRITICAL"

    recommendation="HOLD"

    if risk_state=="DEFENSIVE":
        recommendation="REVIEW_POSITION"

    if risk_state=="CRITICAL":
        recommendation="MANUAL_REVIEW_REQUIRED"

    report={
        "STATUS":"P201_DAILY_DEMO_EVIDENCE_ANALYZED",
        "BALANCE":balance,
        "EQUITY":equity,
        "FLOATING_PNL":pnl,
        "ABSOLUTE_DRAWDOWN":round(dd,2),
        "POSITIONS_TOTAL":data.get("POSITIONS_TOTAL"),
        "RISK_STATE":risk_state,
        "RECOMMENDATION":recommendation,
        "NEW_ORDER_SENT":False,
        "POSITION_CLOSE_SENT":False,
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p201_report.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False),
        encoding="utf-8"
    )

    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
