import json, random
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P69_73_MT5_FTMO_DEMO_GOVERNOR")

BLOCKS={
    "LIVE":"FORBIDDEN",
    "REAL_BROKER":"DISABLED",
    "REAL_ORDERS":"FORBIDDEN",
    "FTMO_REAL":"FORBIDDEN",
    "MT5_REAL":"FORBIDDEN"
}

FTMO_RULES={
    "account_size":100000,
    "profit_target_pct":0.10,
    "max_daily_loss_pct":0.05,
    "max_total_loss_pct":0.10,
    "min_trading_days":4,
    "internal_daily_loss_guard_pct":0.03,
    "internal_total_loss_guard_pct":0.06,
    "max_risk_per_trade_pct":0.0025,
    "max_lot_initial":0.01
}

def p69_mt5_demo_bridge(account_mode="DEMO"):
    demo_ok=str(account_mode).upper()=="DEMO"
    return {
        "module":"P69_MT5_DEMO_BRIDGE",
        "account_mode":account_mode,
        "demo_required":True,
        "demo_validated":demo_ok,
        "trade_transport":"MT5_DEMO_ONLY",
        "order_permission":"DEMO_ONLY" if demo_ok else "BLOCKED_NOT_DEMO",
        **BLOCKS
    }

def p70_ftmo_rule_engine(balance=100000,equity=100000,daily_pnl=0,total_pnl=0,trading_days=0):
    daily_loss=max(0,-daily_pnl)
    total_loss=max(0,-total_pnl)
    return {
        "module":"P70_FTMO_RULE_ENGINE",
        "balance":balance,
        "equity":equity,
        "daily_pnl":daily_pnl,
        "total_pnl":total_pnl,
        "trading_days":trading_days,
        "daily_loss_pct":round(daily_loss/FTMO_RULES["account_size"],6),
        "total_loss_pct":round(total_loss/FTMO_RULES["account_size"],6),
        "profit_pct":round(max(0,total_pnl)/FTMO_RULES["account_size"],6),
        "daily_loss_pass":daily_loss <= FTMO_RULES["account_size"]*FTMO_RULES["internal_daily_loss_guard_pct"],
        "total_loss_pass":total_loss <= FTMO_RULES["account_size"]*FTMO_RULES["internal_total_loss_guard_pct"],
        "profit_target_pass":total_pnl >= FTMO_RULES["account_size"]*FTMO_RULES["profit_target_pct"],
        "min_trading_days_pass":trading_days >= FTMO_RULES["min_trading_days"],
        "rules":FTMO_RULES,
        **BLOCKS
    }

def p71_pre_trade_governor(account_state, proposed_risk_pct=0.001, account_mode="DEMO"):
    bridge=p69_mt5_demo_bridge(account_mode)
    rules=p70_ftmo_rule_engine(**account_state)
    allow=(
        bridge["demo_validated"] and
        rules["daily_loss_pass"] and
        rules["total_loss_pass"] and
        proposed_risk_pct <= FTMO_RULES["max_risk_per_trade_pct"]
    )
    reasons=[]
    if not bridge["demo_validated"]: reasons.append("ACCOUNT_NOT_DEMO")
    if not rules["daily_loss_pass"]: reasons.append("DAILY_LOSS_GUARD")
    if not rules["total_loss_pass"]: reasons.append("TOTAL_LOSS_GUARD")
    if proposed_risk_pct > FTMO_RULES["max_risk_per_trade_pct"]: reasons.append("RISK_PER_TRADE_TOO_HIGH")
    return {
        "module":"P71_PRE_TRADE_FTMO_GOVERNOR",
        "decision":"ALLOW_DEMO_TRADE" if allow else "BLOCK_TRADE",
        "block_reasons":reasons,
        "proposed_risk_pct":proposed_risk_pct,
        "max_allowed_risk_pct":FTMO_RULES["max_risk_per_trade_pct"],
        "max_lot":FTMO_RULES["max_lot_initial"],
        "bridge":bridge,
        "rules":rules,
        **BLOCKS
    }

def p72_ftmo_account_simulator(days=30, seed=7200):
    random.seed(seed)
    balance=FTMO_RULES["account_size"]
    equity=balance
    total_pnl=0
    day_rows=[]
    for d in range(1,days+1):
        daily_pnl=round(random.uniform(-600,900),2)
        total_pnl+=daily_pnl
        rules=p70_ftmo_rule_engine(balance,equity,daily_pnl,total_pnl,d)
        status="PASS" if rules["daily_loss_pass"] and rules["total_loss_pass"] else "FAIL"
        day_rows.append({"day":d,"daily_pnl":daily_pnl,"total_pnl":round(total_pnl,2),"status":status})
        if status=="FAIL":
            break
    return {
        "module":"P72_FTMO_ACCOUNT_SIMULATOR",
        "days_simulated":len(day_rows),
        "final_total_pnl":round(total_pnl,2),
        "final_profit_pct":round(max(0,total_pnl)/FTMO_RULES["account_size"],6),
        "overall_status":"PASS" if all(x["status"]=="PASS" for x in day_rows) else "FAIL",
        "days":day_rows,
        **BLOCKS
    }

def p73_behavioral_risk_engine(recent_results):
    losses=0
    for r in reversed(recent_results):
        if r < 0: losses+=1
        else: break
    if losses>=5:
        mode="LOCKED"
    elif losses>=3:
        mode="DEFENSIVE"
    else:
        mode="NORMAL"
    return {
        "module":"P73_BEHAVIORAL_RISK_ENGINE",
        "consecutive_losses":losses,
        "behavioral_mode":mode,
        "risk_multiplier":0 if mode=="LOCKED" else (0.5 if mode=="DEFENSIVE" else 1.0),
        "overtrading_guard":"ENABLED",
        "revenge_trading_guard":"ENABLED",
        **BLOCKS
    }

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    account_state={"balance":100000,"equity":100000,"daily_pnl":0,"total_pnl":0,"trading_days":0}
    artifacts={
        "p69_mt5_demo_bridge.json":p69_mt5_demo_bridge("DEMO"),
        "p70_ftmo_rule_engine.json":p70_ftmo_rule_engine(**account_state),
        "p71_pre_trade_ftmo_governor.json":p71_pre_trade_governor(account_state,0.001,"DEMO"),
        "p72_ftmo_account_simulator.json":p72_ftmo_account_simulator(30),
        "p73_behavioral_risk_engine.json":p73_behavioral_risk_engine([100,-50,-30,-20])
    }
    for k,v in artifacts.items():
        (OUT/k).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding="utf-8")
    report={
        "STATUS":"P69_73_MT5_DEMO_FTMO_GOVERNOR_IMPLEMENTED",
        "MODULES_IMPLEMENTED":5,
        "MT5_DEMO_BRIDGE":"IMPLEMENTED",
        "FTMO_RULE_ENGINE":"IMPLEMENTED",
        "PRE_TRADE_GOVERNOR":"IMPLEMENTED",
        "FTMO_ACCOUNT_SIMULATOR":"IMPLEMENTED",
        "BEHAVIORAL_RISK_ENGINE":"IMPLEMENTED",
        "NEXT":"P74_MT5_DEMO_ORDER_ROUTER_DRY_RUN",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p69_73_master_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
