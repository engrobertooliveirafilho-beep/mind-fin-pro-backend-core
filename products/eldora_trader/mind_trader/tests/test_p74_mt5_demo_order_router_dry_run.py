from app.p74_mt5_demo_order_router_dry_run.engine import run, build_demo_order, route_order_dry_run

def test_p74_build_order_blocks_real():
    o=build_demo_order()
    assert o["order_mode"]=="DRY_RUN_DEMO_ONLY"
    assert o["REAL_ORDERS"]=="FORBIDDEN"

def test_p74_route_dry_run_does_not_send():
    r=route_order_dry_run(build_demo_order())
    assert r["sent_to_mt5"] is False
    assert r["real_order_sent"] is False

def test_p74_master():
    r=run()
    assert r["STATUS"]=="P74_MT5_DEMO_ORDER_ROUTER_DRY_RUN_IMPLEMENTED"
    assert r["ORDER_SENT"] is False
