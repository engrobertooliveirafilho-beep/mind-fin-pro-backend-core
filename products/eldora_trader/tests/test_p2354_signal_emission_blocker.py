from app.runtime.p2354_signal_emission_blocker import precheck_before_mt5_emit, health

def test_block_bad_signal():
    out = precheck_before_mt5_emit(
        {"symbol":"EURUSD","side":"BUY","strategy":"TREND_EMA","expected_payoff":1.2},
        {"atr":0.5,"adx":10,"spread":4.0,"spread_ok":False,"timeframe":"M1","last_loss":True,"correlation_ok":False,"governance_ok":False}
    )
    assert out["emit_allowed"] is False
    assert out["lot_multiplier"] == 0.0

def test_allow_good_signal():
    out = precheck_before_mt5_emit(
        {"symbol":"EURUSD","side":"BUY","strategy":"SCALP","expected_payoff":3.2},
        {
            "atr":2.0,"adx":25,"spread":1.0,"spread_ok":True,"timeframe":"M1","session":"LONDON",
            "breakout":True,"atr_expansion":True,"volume_impulse":True,
            "m1_confirm":True,"m5_confirm":True,"m1":True,"m5":True,"m15":True,"h1":True,"h1_bias":True,
            "trend_filter":True,"volatility_filter":True,"session_filter":True,"support_resistance_filter":True,
            "last_loss":False,"correlation_ok":True,"governance_ok":True
        }
    )
    assert out["emit_allowed"] is True
    assert out["real_orders"] == "FORBIDDEN"

def test_health():
    assert health()["status"] == "OK"
