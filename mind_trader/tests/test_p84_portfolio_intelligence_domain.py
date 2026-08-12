from app.p84_portfolio_intelligence_domain.engine import run

def test_p84_domain():
    r=run()
    assert r["STATUS"]=="P84_PORTFOLIO_INTELLIGENCE_DOMAIN_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==12
    assert r["REAL_ORDERS"]=="FORBIDDEN"
