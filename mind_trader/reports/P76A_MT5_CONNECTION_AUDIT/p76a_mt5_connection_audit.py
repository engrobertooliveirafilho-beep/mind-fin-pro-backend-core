import json
from pathlib import Path
from datetime import datetime, UTC
import MetaTrader5 as mt5

OUT=Path("reports/P76A_MT5_CONNECTION_AUDIT")

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    initialized=mt5.initialize()
    info=mt5.account_info()
    terminal=mt5.terminal_info()

    account = info._asdict() if info else {}
    term = terminal._asdict() if terminal else {}

    trade_mode = account.get("trade_mode")
    # MT5: 0 real, 1 demo, 2 contest em muitos builds
    demo_ok = trade_mode in [1, "DEMO", "ACCOUNT_TRADE_MODE_DEMO"]

    report={
        "STATUS":"P76A_MT5_CONNECTION_AUDIT_COMPLETED",
        "MT5_INITIALIZED":initialized,
        "ACCOUNT_LOGIN":account.get("login"),
        "ACCOUNT_SERVER":account.get("server"),
        "ACCOUNT_NAME":account.get("name"),
        "ACCOUNT_COMPANY":account.get("company"),
        "ACCOUNT_TRADE_MODE":trade_mode,
        "ACCOUNT_DEMO_VALIDATED":demo_ok,
        "TRADE_ALLOWED":account.get("trade_allowed"),
        "TERMINAL_TRADE_ALLOWED":term.get("trade_allowed"),
        "TERMINAL_CONNECTED":term.get("connected"),
        "TERMINAL_PATH":term.get("path"),
        "NEXT":"P76B_MT5_DEMO_ENVIRONMENT_CERTIFICATION" if initialized and demo_ok else "BLOCKED_NOT_DEMO_OR_NOT_CONNECTED",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "FTMO_REAL":"FORBIDDEN",
        "MT5_REAL":"FORBIDDEN",
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p76a_mt5_account_info.json").write_text(json.dumps(account,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    (OUT/"p76a_mt5_terminal_info.json").write_text(json.dumps(term,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    (OUT/"p76a_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    mt5.shutdown()
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False,default=str))
