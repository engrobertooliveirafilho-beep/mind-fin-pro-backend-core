from app.p18_deep_research_brain.engine import run, research_budget_engine, hypothesis_ranking

def test_p18_research_budget_engine():
    b=research_budget_engine([{"edge_id":"x"}])
    assert b["daily_budget_units"] >= 10
    assert b["max_backtests"] >= 500

def test_p18_hypothesis_ranking():
    r=hypothesis_ranking([{"edge_id":"a","profit_factor":2},{"edge_id":"b","profit_factor":1}])
    assert r[0]["edge_id"]=="a"

def test_p18_deep_research_brain_blocks_live():
    r=run()
    assert r["STATUS"]=="P18_DEEP_RESEARCH_BRAIN_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==10
    assert r["REAL_ORDERS"]=="FORBIDDEN"
