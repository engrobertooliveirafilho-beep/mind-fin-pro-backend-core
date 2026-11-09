from app.p93_120x_extended_demo_ftmo_readiness_runtime.engine import run

def test_p93_120_runtime():
    r=run()
    assert r["STATUS"]=="UNVERIFIED_PENDING_OFFLINE_CERTIFICATION"
    assert r["MODULES_DECLARED"]==28
    assert r["MODULES_CERTIFIED"]==0
    assert r["FTMO_REAL"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
