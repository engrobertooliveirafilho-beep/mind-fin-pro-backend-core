from app.runtime.p2071_2080_realtime_paper_runtime import SignalRuntime, FeatureFrame, PaperPortfolioExecutor

def _frame(rsi=50, close_position=0.5, return_1=0.0005, volatility=0.5):
    return FeatureFrame(ts=100, symbol="XAUUSD", mid=100, spread=0.2, return_1=return_1, volatility_20=volatility, body_to_range=0.1, rsi_14=rsi, stoch_14=50, close_position=close_position)

def _runtime():
    return SignalRuntime([{"specialist_id": "R1", "logic_type": "RANGE_REVERSION"}])

def test_momentum_only_frame_does_not_emit_unexecutable_signal():
    assert _runtime().generate(_frame()) == []

def test_low_rsi_reversion_emits_executable_confidence():
    signals = _runtime().generate(_frame(rsi=30, close_position=0.2))
    assert len(signals) == 1
    assert signals[0].side == "BUY"
    assert signals[0].confidence >= 0.55
    assert PaperPortfolioExecutor().on_signal(signals[0], 100) is not None

def test_high_rsi_reversion_emits_executable_confidence():
    signals = _runtime().generate(_frame(rsi=70, close_position=0.8))
    assert len(signals) == 1
    assert signals[0].side == "SELL"
    assert signals[0].confidence >= 0.55
    assert PaperPortfolioExecutor().on_signal(signals[0], 100) is not None

def test_unsupported_strategy_does_not_generate_signals():
    runtime = SignalRuntime([{"specialist_id":"U1","logic_type":"TREND_PULLBACK"}])
    assert runtime.generate(_frame(rsi=30, close_position=0.2)) == []
