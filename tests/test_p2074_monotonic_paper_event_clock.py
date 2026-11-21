import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperSignal, FeatureFrame

def _signal(ts, specialist="s1"):
    return PaperSignal(ts=ts, symbol="XAUUSD", specialist_id=specialist, side="BUY", confidence=0.9, reason="TEST")

def _frame(ts):
    return FeatureFrame(ts=ts, symbol="XAUUSD", mid=100.0, spread=0.2, return_1=0, volatility_20=0, body_to_range=0, rsi_14=50, stoch_14=50, close_position=0.5)

def test_same_day_older_mark_rejected_without_state_change():
    ex = PaperPortfolioExecutor()
    assert ex.on_signal(_signal(100)) is not None
    ex.mark_to_market(_frame(120))
    before = (ex.equity, ex._last_event_ts, ex._peak_equity, len(ex.positions))
    with pytest.raises(ValueError, match="OUT_OF_ORDER_PAPER_MARK"):
        ex.mark_to_market(_frame(110))
    assert before == (ex.equity, ex._last_event_ts, ex._peak_equity, len(ex.positions))

def test_same_day_older_signal_rejected():
    ex = PaperPortfolioExecutor()
    ex.mark_to_market(_frame(120))
    assert ex.on_signal(_signal(110)) is None
    assert not ex.positions

def test_equal_timestamp_signal_allowed_after_mark():
    ex = PaperPortfolioExecutor()
    ex.mark_to_market(_frame(120))
    assert ex.on_signal(_signal(120)) is not None

def test_next_day_mark_allowed():
    ex = PaperPortfolioExecutor()
    ex.mark_to_market(_frame(86399))
    ex.mark_to_market(_frame(86400))
    assert ex._last_event_ts == 86400
