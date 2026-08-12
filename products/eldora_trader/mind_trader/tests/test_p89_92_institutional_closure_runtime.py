from app.p89_92_institutional_closure_runtime.engine import run

def test_p89_92_closure_runtime():
    r=run()
    assert r["STATUS"]=="P89_92_INSTITUTIONAL_CLOSURE_RUNTIME_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==38
    assert r["FINAL_READINESS"]=="DEMO_OPERATIONAL_READY"
    assert r["FTMO_REAL"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
