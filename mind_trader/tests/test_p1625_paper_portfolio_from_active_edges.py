from app.p1625_paper_portfolio_from_active_edges.engine import run, allocate

def test_p1625_allocate():
    p=allocate([{"profit_factor":2,"max_drawdown":0.1,"decay_revalidation_score":0.1}])
    assert p[0]["paper_weight"] > 0
    assert p[0]["LIVE"]=="FORBIDDEN"

def test_p1625_run_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.25_PAPER_PORTFOLIO_CONSTRUCTION_FROM_ACTIVE_EDGES_IMPLEMENTED"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
