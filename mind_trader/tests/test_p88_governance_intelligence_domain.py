from app.p88_governance_intelligence_domain.engine import run

def test_p88_governance():
    r=run()

    assert r["STATUS"]=="P88_GOVERNANCE_INTELLIGENCE_DOMAIN_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==12
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["FTMO_REAL"]=="FORBIDDEN"
