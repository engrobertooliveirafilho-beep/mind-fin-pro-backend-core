from app.p1626x_institutional_portfolio_intelligence.engine import run, risk_score, allocation_score

def test_p1626x_scores():
    e={"profit_factor":2,"max_drawdown":0.1,"decay_revalidation_score":0.1}
    assert risk_score(e) >= 0
    assert allocation_score(e) > 0

def test_p1626x_runtime_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.26X_INSTITUTIONAL_PORTFOLIO_INTELLIGENCE_RUNTIME_IMPLEMENTED"
    assert r["CERTIFICATION"]=="PAPER_RESEARCH_CERTIFIED"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
