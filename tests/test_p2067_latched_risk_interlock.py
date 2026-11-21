from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperSignal

def _signal(ts=100):
    return PaperSignal(ts=ts, symbol="XAUUSD", specialist_id="RANGE_01", side="BUY", confidence=0.9, reason="OFFLINE_TEST")

def test_total_drawdown_uses_high_water_mark_not_initial_only():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    ex.equity = 110000
    assert ex.on_signal(_signal(), 2400) is not None
    ex.positions.clear()
    ex.equity = 106600
    assert ex.on_signal(_signal(ts=86401), 2400) is None

def test_total_drawdown_breach_stays_locked_after_recovery():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    ex.equity = 96999
    assert ex.on_signal(_signal(), 2400) is None
    ex.equity = 101000
    assert ex.on_signal(_signal(ts=86401), 2400) is None

def test_daily_breach_stays_locked_within_day():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    assert ex.on_signal(_signal(), 2400) is not None
    ex.positions.clear()
    ex.equity = 98999
    assert ex.on_signal(_signal(ts=101), 2400) is None
    ex.equity = 100000
    assert ex.on_signal(_signal(ts=102), 2400) is None

def test_daily_breach_resets_on_next_utc_day():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    assert ex.on_signal(_signal(), 2400) is not None
    ex.positions.clear()
    ex.equity = 98999
    assert ex.on_signal(_signal(ts=101), 2400) is None
    assert ex.on_signal(_signal(ts=86401), 2400) is not None
