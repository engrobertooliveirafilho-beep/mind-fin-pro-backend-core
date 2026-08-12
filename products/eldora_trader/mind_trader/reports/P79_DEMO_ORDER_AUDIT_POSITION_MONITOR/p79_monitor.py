import json
from pathlib import Path
from datetime import datetime, UTC
import MetaTrader5 as mt5

OUT=Path("reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR")

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    mt5.initialize()

    account=mt5.account_info()._asdict() if mt5.account_info() else {}
    terminal=mt5.terminal_info()._asdict() if mt5.terminal_info() else {}
    positions=mt5.positions_get()
    positions_data=[p._asdict() for p in positions] if positions else []

    report={
        "STATUS":"P79_DEMO_ORDER_AUDIT_POSITION_MONITOR_COMPLETED",
        "ACCOUNT_LOGIN":account.get("login"),
        "ACCOUNT_SERVER":account.get("server"),
        "TERMINAL_CONNECTED":terminal.get("connected"),
        "TERMINAL_TRADE_ALLOWED":terminal.get("trade_allowed"),
        "POSITIONS_TOTAL":len(positions_data),
        "POSITIONS":positions_data,
        "ORDER_SENT":False,
        "NEW_ORDER_SENT":False,
        "MONITOR_ONLY":True,
        "NEXT":"P80_DEMO_POSITION_RISK_MONITOR_AND_EXIT_GOVERNOR",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "FTMO_REAL":"FORBIDDEN",
        "MT5_REAL":"FORBIDDEN",
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p79_positions.json").write_text(json.dumps(positions_data,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    (OUT/"p79_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str),encoding="utf-8")

    mt5.shutdown()
    print(json.dumps(report,indent=2,ensure_ascii=False,default=str))

if __name__=="__main__":
    run()
