from app.p75_mt5_demo_order_execution_controlled.engine import run, hard_demo_check, execute_demo_order_controlled

def test_p75_hard_demo_check_blocks_real():
    r=hard_demo_check("REAL")
    assert r["demo_ok"] is False
    assert r["MT5_REAL"]=="FORBIDDEN"

def test_p75_controlled_execution_default_blocked():
    r=execute_demo_order_controlled(account_mode="DEMO", manual_confirmation=True)
    assert r["sent_to_mt5_demo"] is False
    assert r["execution_status"]=="BLOCKED_CONTROLLED_MODE"

def test_p75_master():
    r=run()
    assert r["STATUS"]=="P75_MT5_DEMO_ORDER_EXECUTION_CONTROLLED_IMPLEMENTED"
    assert r["ORDER_SENT"] is False
    assert r["REAL_ORDERS"]=="FORBIDDEN"
