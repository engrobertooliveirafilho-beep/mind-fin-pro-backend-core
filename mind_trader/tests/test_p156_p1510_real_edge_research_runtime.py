from app.p156_p1510_real_edge_research_runtime.engine import backtest, walk_forward, monte_carlo, run

def test_p156_backtest_runs():
    rows=[{"close":float(i)} for i in range(1,200)]
    r=backtest(rows,5,21)
    assert "profit_factor" in r
    assert "trades" in r

def test_p157_walk_forward_safe():
    rows=[{"close":float(i)} for i in range(1,200)]
    r=walk_forward(rows,5,21)
    assert "approved" in r

def test_p158_monte_carlo_safe():
    r=monte_carlo([0.01,-0.005,0.02,-0.01,0.015,0.005,-0.002,0.01,0.003,0.004])
    assert "approved" in r

def test_p1510_manifest():
    m=run()
    assert m["STATUS"]=="P15.6_P15.10_REAL_EDGE_RESEARCH_RUNTIME_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
