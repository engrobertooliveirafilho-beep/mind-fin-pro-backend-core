import json
from pathlib import Path
from datetime import datetime, UTC
import MetaTrader5 as mt5

OUT=Path("reports/P77_DEMO_ORDER_CHECK_ONLY")

def run(symbol="EURUSD", lot=0.01):
    OUT.mkdir(parents=True,exist_ok=True)
    initialized=mt5.initialize()
    account=mt5.account_info()._asdict() if mt5.account_info() else {}
    terminal=mt5.terminal_info()._asdict() if mt5.terminal_info() else {}

    demo_ok=("demo" in str(account.get("server","")).lower()) and ("real" not in str(account.get("server","")).lower())
    env_ok=initialized and demo_ok and terminal.get("connected") and terminal.get("trade_allowed")

    mt5.symbol_select(symbol, True)
    tick=mt5.symbol_info_tick(symbol)
    price=tick.ask if tick else None

    request=None
    check=None

    if env_ok and price:
        request={
            "action":mt5.TRADE_ACTION_DEAL,
            "symbol":symbol,
            "volume":lot,
            "type":mt5.ORDER_TYPE_BUY,
            "price":price,
            "sl":price-0.0010,
            "tp":price+0.0015,
            "deviation":20,
            "magic":770077,
            "comment":"MIND_P77_ORDER_CHECK_ONLY",
            "type_time":mt5.ORDER_TIME_GTC,
            "type_filling":mt5.ORDER_FILLING_IOC
        }
        result=mt5.order_check(request)
        check=result._asdict() if result else None

    report={
        "STATUS":"P77_DEMO_ORDER_CHECK_ONLY_COMPLETED",
        "MT5_INITIALIZED":initialized,
        "ACCOUNT_SERVER":account.get("server"),
        "ACCOUNT_DEMO_VALIDATED":demo_ok,
        "TERMINAL_CONNECTED":terminal.get("connected"),
        "TERMINAL_TRADE_ALLOWED":terminal.get("trade_allowed"),
        "SYMBOL":symbol,
        "LOT":lot,
        "ORDER_CHECK_EXECUTED":check is not None,
        "ORDER_CHECK_RESULT":check,
        "ORDER_SENT":False,
        "NEXT":"P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED" if check else "BLOCKED_ORDER_CHECK_FAILED",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "FTMO_REAL":"FORBIDDEN",
        "MT5_REAL":"FORBIDDEN",
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p77_order_check_request.json").write_text(json.dumps(request,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    (OUT/"p77_order_check_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    mt5.shutdown()
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False,default=str))
