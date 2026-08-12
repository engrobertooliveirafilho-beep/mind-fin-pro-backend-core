from app.p16_autonomous_research_runtime.engine import run, walk_forward_dispatcher, monte_carlo_dispatcher, edge_decay_detector

sample=[{"profit_factor":2.0,"trades":30,"max_drawdown":0.1}]

def test_p16_walk_forward_dispatcher():
    r=walk_forward_dispatcher(sample)
    assert r[0]["LIVE"]=="FORBIDDEN"
    assert "walk_forward_status" in r[0]

def test_p16_monte_carlo_dispatcher():
    r=monte_carlo_dispatcher(sample)
    assert r[0]["REAL_ORDERS"]=="FORBIDDEN"
    assert r[0]["monte_carlo_runs"]==100

def test_p16_edge_decay_detector():
    r=edge_decay_detector([{"profit_factor":2.0,"walk_forward_score":0.6,"monte_carlo_stability":1.4}])
    assert "decay_score" in r[0]

def test_p16_certification_paper_only():
    m=run()
    assert m["STATUS"]=="P16_AUTONOMOUS_RESEARCH_RUNTIME_IMPLEMENTED"
    assert m["LIVE"]=="FORBIDDEN"
    assert m["REAL_BROKER"]=="DISABLED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["FTMO_REAL"]=="FORBIDDEN"
    assert m["CAUSALITY"]=="NOT_PROVEN"
