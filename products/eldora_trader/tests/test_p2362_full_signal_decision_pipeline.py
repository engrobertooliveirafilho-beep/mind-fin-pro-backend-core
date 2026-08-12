from app.runtime.p2362_full_signal_decision_pipeline import decide_signal, health

def test_full_pipeline_emits_good_signal():
    out = decide_signal(
        {"symbol":"EURUSD","side":"BUY","strategy":"SCALP","expected_payoff":3.2,"base_lot":0.01},
        {
            "regime":"TRENDING","cycle":"EARLY","volatility":"HIGH_VOLATILITY","session":"LONDON_OPEN","structure":"BREAKOUT",
            "atr":2.0,"adx":25,"spread":1.0,"spread_ok":True,"timeframe":"M1",
            "breakout":True,"atr_expansion":True,"volume_impulse":True,
            "m1_confirm":True,"m5_confirm":True,"m1":True,"m5":True,"m15":True,"h1":True,"h1_bias":True,
            "trend_filter":True,"volatility_filter":True,"session_filter":True,"support_resistance_filter":True,
            "last_loss":False,"correlation_ok":True,"governance_ok":True,"current_drawdown":2
        }
    )
    assert out["final_decision"] == "EMIT_TO_MT5_PAPER"
    assert out["paper_lot"] > 0
    assert out["real_orders"] == "FORBIDDEN"

def test_full_pipeline_blocks_bad_signal():
    out = decide_signal(
        {"symbol":"EURUSD","side":"BUY","strategy":"TREND_EMA","expected_payoff":1.2,"base_lot":0.01},
        {
            "regime":"RANGING","cycle":"UNKNOWN","volatility":"LOW_VOLATILITY","session":"ASIA","structure":"FAKEOUT",
            "atr":0.4,"adx":10,"spread":5.0,"spread_ok":False,"timeframe":"M1",
            "last_loss":True,"correlation_ok":False,"governance_ok":False,"current_drawdown":12
        }
    )
    assert out["final_decision"] == "BLOCK_SIGNAL"
    assert out["paper_lot"] == 0.0

def test_health():
    assert health()["status"] == "OK"
