import json
from pathlib import Path
from datetime import datetime, UTC
import MetaTrader5 as mt5

OUT=Path("reports/P76B_MT5_DEMO_ENVIRONMENT_CERTIFICATION")
SYMBOLS=["EURUSD","GBPUSD","USDCHF","USDJPY"]

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    initialized=mt5.initialize()
    account=mt5.account_info()._asdict() if mt5.account_info() else {}
    terminal=mt5.terminal_info()._asdict() if mt5.terminal_info() else {}

    symbol_reports=[]
    for s in SYMBOLS:
        info=mt5.symbol_info(s)
        tick=mt5.symbol_info_tick(s)
        visible=False
        if info:
            visible=info.visible or mt5.symbol_select(s, True)
        symbol_reports.append({
            "symbol":s,
            "symbol_exists":info is not None,
            "visible":visible,
            "tick_available":tick is not None,
            "bid":tick.bid if tick else None,
            "ask":tick.ask if tick else None
        })

    demo_ok=("demo" in str(account.get("server","")).lower()) and ("real" not in str(account.get("server","")).lower())
    env_ok=initialized and demo_ok and terminal.get("connected") and terminal.get("trade_allowed")

    report={
        "STATUS":"P76B_MT5_DEMO_ENVIRONMENT_CERTIFICATION_COMPLETED",
        "ENVIRONMENT_CERTIFIED":bool(env_ok),
        "ACCOUNT_LOGIN":account.get("login"),
        "ACCOUNT_SERVER":account.get("server"),
        "ACCOUNT_DEMO_VALIDATED":demo_ok,
        "TERMINAL_CONNECTED":terminal.get("connected"),
        "TERMINAL_TRADE_ALLOWED":terminal.get("trade_allowed"),
        "SYMBOLS_CHECKED":len(symbol_reports),
        "SYMBOLS_READY":len([x for x in symbol_reports if x["symbol_exists"] and x["visible"] and x["tick_available"]]),
        "NEXT":"P77_DEMO_ORDER_CHECK_ONLY" if env_ok else "BLOCKED_ENVIRONMENT_NOT_CERTIFIED",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "FTMO_REAL":"FORBIDDEN",
        "MT5_REAL":"FORBIDDEN",
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p76b_symbols_report.json").write_text(json.dumps(symbol_reports,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p76b_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    mt5.shutdown()
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
