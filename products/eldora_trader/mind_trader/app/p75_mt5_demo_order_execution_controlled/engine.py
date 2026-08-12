import json
from pathlib import Path
from datetime import datetime, UTC
from app.p74_mt5_demo_order_router_dry_run.engine import build_demo_order
from app.p69_73_mt5_ftmo_demo_governor.engine import p71_pre_trade_governor

OUT=Path("reports/P75_MT5_DEMO_ORDER_EXECUTION_CONTROLLED")

BLOCKS={
    "LIVE":"FORBIDDEN",
    "REAL_BROKER":"DISABLED",
    "REAL_ORDERS":"FORBIDDEN",
    "FTMO_REAL":"FORBIDDEN",
    "MT5_REAL":"FORBIDDEN"
}

EXECUTION_ARMED=False

def hard_demo_check(account_mode):
    return {
        "account_mode":account_mode,
        "demo_ok":str(account_mode).upper()=="DEMO",
        "real_blocked":str(account_mode).upper()!="DEMO",
        **BLOCKS
    }

def execute_demo_order_controlled(order=None, account_mode="DEMO", manual_confirmation=False):
    if order is None:
        order=build_demo_order()

    demo=hard_demo_check(account_mode)
    state={"balance":100000,"equity":100000,"daily_pnl":0,"total_pnl":0,"trading_days":0}
    gov=p71_pre_trade_governor(state,0.001,account_mode)

    allowed = (
        EXECUTION_ARMED is True and
        manual_confirmation is True and
        demo["demo_ok"] is True and
        gov["decision"]=="ALLOW_DEMO_TRADE" and
        float(order.get("lot",0)) <= 0.01
    )

    result={
        "module":"P75_MT5_DEMO_ORDER_EXECUTION_CONTROLLED",
        "execution_armed":EXECUTION_ARMED,
        "manual_confirmation":manual_confirmation,
        "demo_check":demo,
        "governor_decision":gov["decision"],
        "order":order,
        "sent_to_mt5_demo":allowed,
        "execution_status":"DEMO_ORDER_SENT" if allowed else "BLOCKED_CONTROLLED_MODE",
        "reason":"Requires EXECUTION_ARMED=True, manual_confirmation=True, DEMO account, governor approval, lot<=0.01",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    return result

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    result=execute_demo_order_controlled()
    (OUT/"p75_controlled_execution_audit.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    report={
        "STATUS":"P75_MT5_DEMO_ORDER_EXECUTION_CONTROLLED_IMPLEMENTED",
        "EXECUTION_ARMED":EXECUTION_ARMED,
        "ORDER_SENT":result["sent_to_mt5_demo"],
        "NEXT":"P76_MT5_DEMO_EXECUTION_ARMING_PROCEDURE",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p75_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
