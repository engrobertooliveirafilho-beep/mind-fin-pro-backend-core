import json
from pathlib import Path
from datetime import datetime, UTC
from app.p69_73_mt5_ftmo_demo_governor.engine import p71_pre_trade_governor

OUT=Path("reports/P74_MT5_DEMO_ORDER_ROUTER_DRY_RUN")

BLOCKS={
    "LIVE":"FORBIDDEN",
    "REAL_BROKER":"DISABLED",
    "REAL_ORDERS":"FORBIDDEN",
    "FTMO_REAL":"FORBIDDEN",
    "MT5_REAL":"FORBIDDEN"
}

def build_demo_order(symbol="EURUSD", side="BUY", lot=0.01, sl_points=100, tp_points=150):
    return {
        "symbol":symbol,
        "side":side,
        "lot":lot,
        "sl_points":sl_points,
        "tp_points":tp_points,
        "order_mode":"DRY_RUN_DEMO_ONLY",
        **BLOCKS
    }

def route_order_dry_run(order, account_state=None, account_mode="DEMO"):
    if account_state is None:
        account_state={"balance":100000,"equity":100000,"daily_pnl":0,"total_pnl":0,"trading_days":0}
    proposed_risk_pct=0.001
    governor=p71_pre_trade_governor(account_state, proposed_risk_pct, account_mode)
    status="DRY_RUN_APPROVED_NOT_SENT" if governor["decision"]=="ALLOW_DEMO_TRADE" else "DRY_RUN_BLOCKED"
    return {
        "router":"P74_MT5_DEMO_ORDER_ROUTER_DRY_RUN",
        "order":order,
        "governor_decision":governor["decision"],
        "status":status,
        "sent_to_mt5":False,
        "real_order_sent":False,
        "audit":"NO_ORDER_TRANSMISSION_IN_P74",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    order=build_demo_order()
    result=route_order_dry_run(order)
    (OUT/"p74_demo_order_payload.json").write_text(json.dumps(order,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p74_dry_run_audit.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    report={
        "STATUS":"P74_MT5_DEMO_ORDER_ROUTER_DRY_RUN_IMPLEMENTED",
        "ORDER_ROUTER":"DRY_RUN_ONLY",
        "ORDER_SENT":False,
        "NEXT":"P75_MT5_DEMO_ORDER_EXECUTION_CONTROLLED",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p74_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
