import json
from pathlib import Path
from datetime import datetime, UTC
import MetaTrader5 as mt5

OUT=Path("reports/P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED")

def run(symbol="EURUSD", lot=0.01):
    OUT.mkdir(parents=True,exist_ok=True)

    mt5.initialize()
    account=mt5.account_info()._asdict()
    terminal=mt5.terminal_info()._asdict()

    server=str(account.get("server","")).lower()
    demo_ok=("demo" in server) and ("real" not in server)
    terminal_ok=terminal.get("connected") and terminal.get("trade_allowed")

    if not demo_ok or not terminal_ok or lot > 0.01:
        report={
            "STATUS":"P78_BLOCKED",
            "REASON":"DEMO_REQUIRED_OR_TERMINAL_NOT_ALLOWED_OR_LOT_TOO_HIGH",
            "ORDER_SENT":False,
            "LIVE":"FORBIDDEN",
            "REAL_ORDERS":"FORBIDDEN",
            "FTMO_REAL":"FORBIDDEN",
            "MT5_REAL":"FORBIDDEN"
        }
        (OUT/"p78_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
        mt5.shutdown()
        print(json.dumps(report,indent=2,ensure_ascii=False))
        return

    mt5.symbol_select(symbol, True)
    tick=mt5.symbol_info_tick(symbol)
    price=tick.ask

    request={
        "action":mt5.TRADE_ACTION_DEAL,
        "symbol":symbol,
        "volume":lot,
        "type":mt5.ORDER_TYPE_BUY,
        "price":price,
        "sl":price-0.0010,
        "tp":price+0.0015,
        "deviation":20,
        "magic":780078,
        "comment":"MIND_P78_DEMO_ONLY",
        "type_time":mt5.ORDER_TIME_GTC,
        "type_filling":mt5.ORDER_FILLING_FOK
    }

    check=mt5.order_check(request)
    result=None

    if check and check.retcode==0:
        result=mt5.order_send(request)

    report={
        "STATUS":"P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED_COMPLETED",
        "ACCOUNT_LOGIN":account.get("login"),
        "ACCOUNT_SERVER":account.get("server"),
        "ACCOUNT_DEMO_VALIDATED":demo_ok,
        "SYMBOL":symbol,
        "LOT":lot,
        "ORDER_CHECK_RETCODE":check.retcode if check else None,
        "ORDER_SEND_RETCODE":result.retcode if result else None,
        "ORDER_SEND_COMMENT":result.comment if result else None,
        "ORDER_SENT":bool(result and result.retcode in [10008,10009]),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "FTMO_REAL":"FORBIDDEN",
        "MT5_REAL":"FORBIDDEN",
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p78_order_request.json").write_text(json.dumps(request,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    (OUT/"p78_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str),encoding="utf-8")

    mt5.shutdown()
    print(json.dumps(report,indent=2,ensure_ascii=False,default=str))

if __name__=="__main__":
    run()
