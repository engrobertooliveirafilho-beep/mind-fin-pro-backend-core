from app.p93_120x_extended_demo_ftmo_readiness_runtime.engine import run

def test_p93_120_runtime():
    r=run()
    assert r["STATUS"]=="P93_120X_EXTENDED_DEMO_FTMO_READINESS_RUNTIME_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==28
    assert r["FTMO_REAL"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
