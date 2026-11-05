import sys
import types

module = types.ModuleType("app.runtime.p2353_signal_precheck_institutional_score")
module.institutional_signal_score = lambda signal, context: {
    "decision": "APPROVE",
    "institutional_score": 90,
    "lot_multiplier": 1.0,
    "reasons": [],
}
sys.modules[module.__name__] = module

from app.runtime.p2354_signal_emission_blocker import precheck_before_mt5_emit


def _signal(side, candle="20260622_11_H1", symbol="GER40"):
    return {"symbol": symbol, "timeframe": "H1", "candle_key": candle, "side": side}


def test_opposite_same_candle_blocked():
    signal = _signal("BUY")
    result = precheck_before_mt5_emit(signal, {
        "candidate_signals": [signal, _signal("SELL")],
    })
    assert result["emit_allowed"] is False
    assert result["decision"] == "BLOCK_CONFLICTING_DIRECTIONS_SAME_CANDLE"
    assert result["real_orders"] == "FORBIDDEN"


def test_same_direction_allowed_to_existing_score():
    signal = _signal("BUY")
    result = precheck_before_mt5_emit(signal, {
        "candidate_signals": [signal, _signal("BUY")],
    })
    assert result["emit_allowed"] is True


def test_different_candle_not_conflict():
    signal = _signal("BUY")
    result = precheck_before_mt5_emit(signal, {
        "candidate_signals": [signal, _signal("SELL", "20260622_12_H1")],
    })
    assert result["emit_allowed"] is True


def test_missing_batch_key_fail_closed():
    result = precheck_before_mt5_emit({"symbol": "GER40", "side": "BUY"}, {
        "candidate_signals": [_signal("SELL")],
    })
    assert result["emit_allowed"] is False


def test_legacy_single_signal_compatibility():
    assert precheck_before_mt5_emit(_signal("BUY"), {})["emit_allowed"] is True
