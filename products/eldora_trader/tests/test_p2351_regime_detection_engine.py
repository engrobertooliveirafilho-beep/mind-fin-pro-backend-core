from app.runtime.p2351_regime_detection_engine import detect_regime, approve_strategy_for_regime

def test_trending_regime_approves_trend():
    out = approve_strategy_for_regime("TREND_EMA", {
        "atr": 2.0, "adx": 30, "spread": 1.0, "timeframe": "M5", "session": "LONDON"
    })
    assert out["regime"] == "TRENDING"
    assert out["approved"] is True
    assert out["target_payoff_min"] == 3.0
    assert out["real_orders"] == "FORBIDDEN"

def test_ranging_blocks_trend():
    out = approve_strategy_for_regime("TREND_EMA", {
        "atr": 0.8, "adx": 12, "spread": 1.0, "timeframe": "M5"
    })
    assert out["regime"] == "RANGING"
    assert out["decision"] == "BLOCK"

def test_scalp_requires_spread_ok():
    out = approve_strategy_for_regime("SCALP", {
        "atr": 1.0, "adx": 20, "spread": 1.0, "timeframe": "M1"
    })
    assert out["approved"] is True
