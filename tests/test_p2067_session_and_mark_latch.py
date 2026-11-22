from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperSignal, PaperPosition, FeatureFrame

def _signal(ts):
    return PaperSignal(ts=ts, symbol="XAUUSD", specialist_id="B", side="BUY", confidence=0.9, reason="TEST")

def _frame(ts, mid):
    return FeatureFrame(ts=ts, symbol="XAUUSD", mid=mid, spread=0.2, return_1=0, volatility_20=0, body_to_range=0, rsi_14=50, stoch_14=50, close_position=0.5)

def test_out_of_order_session_rejected():
    ex = PaperPortfolioExecutor()
    assert ex.on_signal(_signal(86401), 100) is not None
    assert ex.on_signal(_signal(100), 100) is None

def test_invalid_session_timestamp_rejected():
    ex = PaperPortfolioExecutor()
    for ts in (-1, 0.5, True, "100"):
        assert ex.on_signal(_signal(ts), 100) is None

def test_mark_to_market_latches_daily_breach_before_next_signal():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    assert ex.on_signal(_signal(100), 2400) is not None
    ex.positions.clear()
    ex.positions["A"] = PaperPosition(position_id="A", symbol="XAUUSD", specialist_id="A", side="BUY", entry=2000, sl=-10000, tp=20000, qty=1, open_ts=100)
    ex.mark_to_market(_frame(101, 900))
    ex.positions.clear()
    assert ex.on_signal(_signal(102), 2400) is None
