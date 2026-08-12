from app.runtime.p2366_institutional_targeting_engine import institutional_targets, health

def test_buy_target_approved_above_2r():
    out=institutional_targets({
        "side":"BUY","entry":100,"stop":98,
        "swing_high":102,"swing_low":98,
        "atr":2,"session_high":104,"liquidity_high":104,
        "vwap":101,"round_number":104,
    })
    assert out["approved"] is True
    assert out["rr"] >= 2.0
    assert out["real_orders"] == "FORBIDDEN"

def test_sell_target_approved_above_2r():
    out=institutional_targets({
        "side":"SELL","entry":100,"stop":102,
        "swing_high":102,"swing_low":98,
        "atr":2,"session_low":96,"liquidity_low":96,
        "vwap":99,"round_number":96,
    })
    assert out["approved"] is True
    assert out["rr"] >= 2.0

def test_blocks_below_2r():
    out=institutional_targets({
        "side":"BUY","entry":100,"stop":98,
        "swing_high":100.5,"swing_low":99.5,
        "atr":0.2,"session_high":101,"liquidity_high":101,
        "vwap":100,"round_number":101,
    })
    assert out["approved"] is False
    assert out["decision"] == "BLOCK_TARGET_BELOW_2R"

def test_health():
    assert health()["target_min_rr"] == 2.0
