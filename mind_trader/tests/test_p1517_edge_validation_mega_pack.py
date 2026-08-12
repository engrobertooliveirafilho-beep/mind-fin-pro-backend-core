from app.p1517_edge_validation_mega_pack.engine import regime, validate_edge, web_research_queue_summary, run

def test_p1517_regime():
    assert regime({"profit_factor":2.1,"trades":40,"winrate":38}) in ("strong_trend","asymmetric_payoff","stable_reversion","mixed")

def test_p1517_validate_edge_blocks_live():
    e={"symbol":"IFIX","timeframe":"H1","strategy":"sma_cross","profit_factor":2.0,"trades":50,"walk_forward_approved":True,"monte_carlo_approved":True}
    r=validate_edge(e,[e])
    assert r["real_orders"]=="FORBIDDEN"
    assert "validation_score" in r

def test_p1517_web_summary():
    s=web_research_queue_summary()
    assert s["requires_backtest"] is True

def test_p1517_manifest():
    m=run()
    assert m["STATUS"]=="P15.17_EDGE_VALIDATION_MEGA_PACK_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
