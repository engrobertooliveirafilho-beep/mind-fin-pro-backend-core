from app.runtime.p2356_context_regime_edge_engine import classify_context_edge, score_context_edge, health

def test_trending_breakout_context_edge():
    out = classify_context_edge({
        "regime": "TRENDING",
        "cycle": "EARLY",
        "volatility": "HIGH_VOLATILITY",
        "session": "LONDON_OPEN",
        "structure": "BREAKOUT",
    })
    assert out["edge_type"] == "TRENDING_BREAKOUT"
    assert out["symbol_is_validation_field"] is True

def test_promotes_context_edge_not_symbol_edge():
    out = score_context_edge({
        "trades": 80,
        "win_rate": 62,
        "payoff": 3.2,
        "profit_factor": 2.1,
        "expectancy": 0.8,
        "max_drawdown": 6,
    })
    assert out["passed"] is True
    assert out["decision"] == "PROMOTE_CONTEXT_EDGE"

def test_health():
    assert health()["status"] == "OK"
