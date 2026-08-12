from app.p87_edge_intelligence_domain.engine import run, edge_score

def test_p87_edge_score():
    s=edge_score({"profit_factor":2,"max_drawdown":0.1,"trades":60})
    assert s > 0

def test_p87_edge_domain():
    r=run()
    assert r["STATUS"]=="P87_EDGE_INTELLIGENCE_DOMAIN_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==8
    assert r["REAL_ORDERS"]=="FORBIDDEN"
