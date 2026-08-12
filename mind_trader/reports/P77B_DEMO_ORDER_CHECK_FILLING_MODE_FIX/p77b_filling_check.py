import json
from pathlib import Path
from datetime import datetime, UTC
import MetaTrader5 as mt5

OUT=Path("reports/P77B_DEMO_ORDER_CHECK_FILLING_MODE_FIX")

FILLINGS=[
    ("FOK", mt5.ORDER_FILLING_FOK),
    ("IOC", mt5.ORDER_FILLING_IOC),
    ("RETURN", mt5.ORDER_FILLING_RETURN)
]

def check(symbol="EURUSD", lot=0.01):
    mt5.initialize()
    account=mt5.account_info()._asdict()
    terminal=mt5.terminal_info()._asdict()
    mt5.symbol_select(symbol, True)
    tick=mt5.symbol_info_tick(symbol)
    price=tick.ask if tick else None

    results=[]
    for name, filling in FILLINGS:
        req={
            "action":mt5.TRADE_ACTION_DEAL,
            "symbol":symbol,
            "volume":lot,
            "type":mt5.ORDER_TYPE_BUY,
            "price":price,
            "sl":price-0.0010,
            "tp":price+0.0015,
            "deviation":20,
            "magic":770077,
            "comment":"MIND_P77B_FILLING_CHECK",
            "type_time":mt5.ORDER_TIME_GTC,
            "type_filling":filling
        }
        r=mt5.order_check(req)
        results.append({
            "filling_name":name,
            "filling_value":filling,
            "retcode":r.retcode if r else None,
            "comment":r.comment if r else None,
            "approved":bool(r and r.retcode==0),
            "request":req
        })

    approved=[x for x in results if x["approved"]]
    report={
        "STATUS":"P77B_DEMO_ORDER_CHECK_FILLING_MODE_FIX_COMPLETED",
        "ACCOUNT_SERVER":account.get("server"),
        "TERMINAL_CONNECTED":terminal.get("connected"),
        "TERMINAL_TRADE_ALLOWED":terminal.get("trade_allowed"),
        "SYMBOL":symbol,
        "LOT":lot,
        "FILLING_RESULTS":results,
        "APPROVED_FILLING":approved[0]["filling_name"] if approved else None,
        "APPROVED_FILLING_VALUE":approved[0]["filling_value"] if approved else None,
        "ORDER_CHECK_APPROVED":len(approved)>0,
        "ORDER_SENT":False,
        "NEXT":"P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED" if approved else "BLOCKED_NO_SUPPORTED_FILLING",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "FTMO_REAL":"FORBIDDEN",
        "MT5_REAL":"FORBIDDEN",
        "generated_at":datetime.now(UTC).isoformat()
    }

    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"p77b_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
    mt5.shutdown()
    return report

if __name__=="__main__":
    print(json.dumps(check(),indent=2,ensure_ascii=False,default=str))
