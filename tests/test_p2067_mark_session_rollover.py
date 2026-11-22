import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperSignal, FeatureFrame

def _frame(ts, mid=2400.0):
    return FeatureFrame(ts=ts, symbol="XAUUSD", mid=mid, spread=0.2, return_1=0, volatility_20=0, body_to_range=0, rsi_14=50, stoch_14=50, close_position=0.5)

def _signal(ts):
    return PaperSignal(ts=ts, symbol="XAUUSD", specialist_id="S1", side="BUY", confidence=0.9, reason="TEST")

def test_mark_initializes_utc_day_before_first_signal():
    ex = PaperPortfolioExecutor()
    ex.mark_to_market(_frame(86401))
    assert ex._paper_day == 1
    assert ex._day_start_equity == ex.equity

def test_mark_rollover_resets_daily_latch_not_total_latch():
    ex = PaperPortfolioExecutor()
    ex.mark_to_market(_frame(100))
    ex._daily_risk_locked = True
    ex._risk_locked = True
    ex.mark_to_market(_frame(86401))
    assert not ex._daily_risk_locked
    assert ex._risk_locked

def test_mark_rejects_backward_session():
    ex = PaperPortfolioExecutor()
    ex.mark_to_market(_frame(86401))
    with pytest.raises(ValueError, match="OUT_OF_ORDER_PAPER_MARK"):
        ex.mark_to_market(_frame(100))

def test_mark_rejects_invalid_timestamp():
    ex = PaperPortfolioExecutor()
    for ts in (-1, 0.5, True, "123"):
        with pytest.raises(ValueError, match="INVALID_PAPER_MARK_TIMESTAMP"):
            ex.mark_to_market(_frame(ts))

def test_signal_after_mark_rollover_does_not_reset_daily_baseline():
    ex = PaperPortfolioExecutor()
    ex.mark_to_market(_frame(86401))
    ex._day_start_equity = 100000
    ex.equity = 98999
    assert ex.on_signal(_signal(86402), 2400) is None
