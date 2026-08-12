from app.p1519_p1525_institutional_research_certification.engine import max_drawdown, risk_of_ruin, corr, run

def test_p1519_drawdown():
    assert max_drawdown([1.1,1.0,1.2]) >= 0

def test_p1521_risk_blocks():
    r=risk_of_ruin([{"return":0.1},{"return":-0.02},{"return":0.03}])
    assert "risk_proxy" in r

def test_p1520_corr():
    assert corr([1,2,3],[1,2,3]) >= 0.99

def test_p1525_manifest():
    m=run()
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
