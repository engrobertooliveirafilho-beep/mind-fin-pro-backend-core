from app.p18_21x_unified_institutional_intelligence.engine import run

def test_p18_21x_unified_runtime():
    r=run()
    assert r["STATUS"]=="P18_21X_UNIFIED_INSTITUTIONAL_INTELLIGENCE_RUNTIME_IMPLEMENTED"
    assert r["MODULES_CONSOLIDATED"]==47
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["CAUSALITY"]=="PARTIALLY_PROVEN"
