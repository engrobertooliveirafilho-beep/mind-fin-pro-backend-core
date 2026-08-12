from app.p85_risk_intelligence_domain.engine import run, kill_switch

def test_p85_kill_switch_safe():
    r=kill_switch([{"profit":-0.16,"volume":0.01}])
    assert r["kill_switch_active"] is False
    assert r["REAL_ORDERS"]=="FORBIDDEN"

def test_p85_risk_domain():
    r=run()
    assert r["STATUS"]=="P85_RISK_INTELLIGENCE_DOMAIN_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==10
    assert r["FTMO_REAL"]=="FORBIDDEN"
