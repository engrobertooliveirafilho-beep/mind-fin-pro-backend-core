import csv
from app.p151_real_edge_discovery_runtime.engine import score, run, BACKTEST_DIR

def test_p151_score_good_candidate():
    r=score({"profit_factor":"1.6","trades":"300","drawdown":"1000","payoff":"0.7","winrate":"52"})
    assert r["edge_candidate"] is True
    assert r["real_orders"]=="FORBIDDEN"

def test_p151_score_rejects_bad_candidate():
    r=score({"profit_factor":"0.8","trades":"20","drawdown":"9000","payoff":"-1","winrate":"40"})
    assert r["edge_candidate"] is False

def test_p151_manifest():
    m=run()
    assert m["STATUS"]=="P15.1_REAL_EDGE_DISCOVERY_RUNTIME_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
