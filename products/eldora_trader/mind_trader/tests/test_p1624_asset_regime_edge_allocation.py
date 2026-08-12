from app.p1624_asset_regime_edge_allocation.engine import run, score

def test_p1624_score():
    assert score({"profit_factor":2,"trades":40,"max_drawdown":0.1,"decay_revalidation_score":0.2}) > 0

def test_p1624_run_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.24_ASSET_REGIME_EDGE_ALLOCATION_ENGINE_IMPLEMENTED"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
