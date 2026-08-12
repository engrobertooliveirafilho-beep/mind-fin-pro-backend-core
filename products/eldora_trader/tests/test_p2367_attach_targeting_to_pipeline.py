from app.runtime.p2362_full_signal_decision_pipeline import decide_signal, health

def good_context():
    return {
        "regime":"TRENDING","cycle":"EARLY","volatility":"HIGH_VOLATILITY","session":"LONDON_OPEN","structure":"BREAKOUT",
        "atr":2.0,"adx":25,"spread":1.0,"spread_ok":True,"timeframe":"M1",
        "breakout":True,"atr_expansion":True,"volume_impulse":True,
        "m1_confirm":True,"m5_confirm":True,"m1":True,"m5":True,"m15":True,"h1":True,"h1_bias":True,
        "trend_filter":True,"volatility_filter":True,"session_filter":True,"support_resistance_filter":True,
        "last_loss":False,"correlation_ok":True,"governance_ok":True,"current_drawdown":2,
        "entry":100,"stop":98,"swing_high":102,"swing_low":98,
        "session_high":104,"liquidity_high":104,"vwap":101,"round_number":104
    }

def test_pipeline_blocks_target_below_2r():
    ctx = good_context()
    ctx.update({"entry":100,"stop":98,"swing_high":100.5,"swing_low":99.5,"atr":0.2,"session_high":101,"liquidity_high":101,"vwap":100,"round_number":101})
    out = decide_signal({"symbol":"DE40","side":"BUY","strategy":"SCALP","base_lot":0.01}, ctx)
    assert out["final_decision"] == "BLOCK_SIGNAL_TARGET_BELOW_2R"
    assert out["paper_lot"] == 0.0

def test_pipeline_emits_when_target_and_institutional_score_pass():
    out = decide_signal({"symbol":"DE40","side":"BUY","strategy":"SCALP","base_lot":0.01}, good_context())
    assert out["targeting"]["approved"] is True
    assert out["targeting"]["rr"] >= 2.0
    assert out["final_decision"] == "EMIT_TO_MT5_PAPER"
    assert out["paper_lot"] > 0
    assert out["real_orders"] == "FORBIDDEN"

def test_health():
    assert health()["target_min_rr"] == 2.0
