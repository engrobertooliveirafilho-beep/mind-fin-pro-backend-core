from app.p69_73_mt5_ftmo_demo_governor.engine import p69_mt5_demo_bridge, p71_pre_trade_governor, p73_behavioral_risk_engine, run

def test_p69_blocks_non_demo():
    r=p69_mt5_demo_bridge("REAL")
    assert r["order_permission"]=="BLOCKED_NOT_DEMO"
    assert r["MT5_REAL"]=="FORBIDDEN"

def test_p71_pre_trade_governor_allows_demo_low_risk():
    state={"balance":100000,"equity":100000,"daily_pnl":0,"total_pnl":0,"trading_days":0}
    r=p71_pre_trade_governor(state,0.001,"DEMO")
    assert r["decision"]=="ALLOW_DEMO_TRADE"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

def test_p73_behavioral_defensive_mode():
    r=p73_behavioral_risk_engine([100,-1,-2,-3])
    assert r["behavioral_mode"]=="DEFENSIVE"

def test_p69_73_master_runtime():
    r=run()
    assert r["STATUS"]=="P69_73_MT5_DEMO_FTMO_GOVERNOR_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==5
    assert r["FTMO_REAL"]=="FORBIDDEN"

