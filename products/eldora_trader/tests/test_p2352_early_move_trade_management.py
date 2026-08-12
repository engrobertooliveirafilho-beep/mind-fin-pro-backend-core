from app.runtime.p2352_early_move_trade_management import detect_early_move, manage_trade, health

def test_early_move_approved():
    out = detect_early_move({
        "adx": 25,
        "atr_expansion": True,
        "breakout": True,
        "volume_impulse": True,
        "m1_confirm": True,
        "m5_confirm": True,
        "h1_bias": True,
        "spread_ok": True,
    })
    assert out["decision"] == "EARLY_ENTRY_APPROVED"
    assert out["target_payoff_min"] == 3.0
    assert out["real_orders"] == "FORBIDDEN"

def test_trade_management_partial_and_breakeven():
    out = manage_trade({"r_multiple": 1.2, "open_parts": 1.0})
    assert "TAKE_PARTIAL_50" in out["actions"]
    assert "MOVE_STOP_TO_BREAKEVEN" in out["actions"]

def test_trade_management_rebuild_only_valid_pullback():
    out = manage_trade({"r_multiple": 2.5, "trend_continues": True, "pullback_valid": True})
    assert "REBUILD_POSITION_SMALL_SIZE" in out["actions"]

def test_health():
    assert health()["status"] == "OK"
