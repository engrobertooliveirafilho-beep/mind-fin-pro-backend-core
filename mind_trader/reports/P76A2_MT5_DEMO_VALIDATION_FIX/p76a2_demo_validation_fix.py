import json
from pathlib import Path
from datetime import datetime, UTC
import MetaTrader5 as mt5

OUT=Path("reports/P76A2_MT5_DEMO_VALIDATION_FIX")

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    initialized=mt5.initialize()
    info=mt5.account_info()
    terminal=mt5.terminal_info()

    account=info._asdict() if info else {}
    term=terminal._asdict() if terminal else {}

    server=str(account.get("server","")).lower()
    company=str(account.get("company","")).lower()
    name=str(account.get("name","")).lower()

    demo_by_server=("demo" in server) or ("demo" in company)
    contest_by_server=("contest" in server) or ("contest" in company)
    real_suspected=("real" in server) or ("real" in company)

    demo_validated = initialized and demo_by_server and not real_suspected

    report={
        "STATUS":"P76A2_MT5_DEMO_VALIDATION_FIX_COMPLETED",
        "MT5_INITIALIZED":initialized,
        "ACCOUNT_LOGIN":account.get("login"),
        "ACCOUNT_SERVER":account.get("server"),
        "ACCOUNT_COMPANY":account.get("company"),
        "ACCOUNT_TRADE_MODE_RAW":account.get("trade_mode"),
        "DEMO_BY_SERVER_OR_COMPANY":demo_by_server,
        "CONTEST_BY_SERVER_OR_COMPANY":contest_by_server,
        "REAL_SUSPECTED":real_suspected,
        "ACCOUNT_DEMO_VALIDATED":demo_validated,
        "ACCOUNT_TRADE_ALLOWED":account.get("trade_allowed"),
        "TERMINAL_TRADE_ALLOWED":term.get("trade_allowed"),
        "TERMINAL_CONNECTED":term.get("connected"),
        "AUTO_TRADING_REQUIRED": term.get("trade_allowed") is True,
        "NEXT":"P76B_MT5_DEMO_ENVIRONMENT_CERTIFICATION" if demo_validated else "BLOCKED_DEMO_NOT_CONFIRMED",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "FTMO_REAL":"FORBIDDEN",
        "MT5_REAL":"FORBIDDEN",
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p76a2_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    mt5.shutdown()
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False,default=str))
