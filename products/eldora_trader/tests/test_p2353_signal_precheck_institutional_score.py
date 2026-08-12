from app.runtime.p2353_signal_precheck_institutional_score import institutional_signal_score, health

def test_priority_signal():
    out = institutional_signal_score(
        {"symbol": "EURUSD", "side": "BUY", "strategy": "SCALP", "expected_payoff": 3.2},
        {
            "atr": 2.0, "adx": 25, "spread": 1.0, "spread_ok": True,
            "timeframe": "M1", "session": "LONDON",
            "breakout": True, "atr_expansion": True, "volume_impulse": True,
            "m1_confirm": True, "m5_confirm": True, "m15": True, "h1": True,
            "m5": True, "m1": True, "h1_bias": True,
            "trend_filter": True, "volatility_filter": True,
            "session_filter": True, "support_resistance_filter": True,
            "last_loss": False, "correlation_ok": True, "governance_ok": True,
        }
    )
    assert out["decision"] in {"APPROVE", "PRIORITY"}
    assert out["institutional_score"] >= 75
    assert out["real_orders"] == "FORBIDDEN"

def test_blocks_low_payoff_bad_context():
    out = institutional_signal_score(
        {"symbol": "EURUSD", "side": "BUY", "strategy": "TREND_EMA", "expected_payoff": 1.5},
        {
            "atr": 0.5, "adx": 10, "spread": 4.0, "spread_ok": False,
            "timeframe": "M1", "last_loss": True,
            "correlation_ok": False, "governance_ok": False,
        }
    )
    assert out["decision"] == "BLOCK"

def test_health():
    assert health()["status"] == "OK"
