import json
from pathlib import Path
from datetime import datetime, UTC
import MetaTrader5 as mt5

OUT=Path("reports/DAILY_DEMO_EVIDENCE_COLLECTION")
BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"daily").mkdir(parents=True,exist_ok=True)

    mt5.initialize()
    account=mt5.account_info()._asdict() if mt5.account_info() else {}
    terminal=mt5.terminal_info()._asdict() if mt5.terminal_info() else {}
    positions=mt5.positions_get()
    positions=[p._asdict() for p in positions] if positions else []
    mt5.shutdown()

    floating=sum(float(p.get("profit") or 0) for p in positions)

    report={
        "STATUS":"DAILY_DEMO_EVIDENCE_COLLECTED",
        "ACCOUNT_LOGIN":account.get("login"),
        "ACCOUNT_SERVER":account.get("server"),
        "BALANCE":account.get("balance"),
        "EQUITY":account.get("equity"),
        "TERMINAL_CONNECTED":terminal.get("connected"),
        "POSITIONS_TOTAL":len(positions),
        "FLOATING_PNL":round(floating,6),
        "POSITIONS":positions,
        "NEW_ORDER_SENT":False,
        "POSITION_CLOSE_SENT":False,
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    stamp=datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    (OUT/"daily"/f"demo_evidence_{stamp}.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    (OUT/"latest_demo_evidence.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False,default=str))

if __name__=="__main__":
    run()
