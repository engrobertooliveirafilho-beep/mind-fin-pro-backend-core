from app.modules.usde_core.monte_carlo_engine import MonteCarloEngine

def test_monte_carlo_simulate():
    r=MonteCarloEngine().simulate(list(range(1,26)),15,1000)
    assert r["trials"]==1000

def test_monte_carlo_compare():
    r=MonteCarloEngine().compare(0.60,0.50)
    assert r["better_than_baseline"] is True
