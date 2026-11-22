from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperSignal

def signal(ts=100, sid="XAUUSD_M1_REALDNA_0004"):
    return PaperSignal(ts=ts, symbol="XAUUSD", specialist_id=sid, side="BUY", confidence=0.9, reason="OFFLINE_TEST")

def test_p2067_daily_realized_loss_blocks_new_entries():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    assert ex.on_signal(signal(), 2400) is not None
    ex.positions.clear()
    ex.equity = 98999.0
    assert ex.on_signal(signal(ts=101), 2400) is None

def test_p2067_total_realized_drawdown_blocks_new_entries():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    ex.equity = 96999.0
    assert ex.on_signal(signal(), 2400) is None

def test_p2067_new_utc_day_resets_daily_baseline_but_not_total_drawdown():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    assert ex.on_signal(signal(ts=100), 2400) is not None
    ex.positions.clear()
    ex.equity = 98999.0
    assert ex.on_signal(signal(ts=101), 2400) is None
    assert ex.on_signal(signal(ts=86401), 2400) is not None

def test_p2067_prevents_concurrent_duplicate_specialist():
    ex = PaperPortfolioExecutor()
    assert ex.on_signal(signal(), 2400) is not None
    assert ex.on_signal(signal(ts=101), 2401) is None
    assert len(ex.positions) == 1

def test_p2067_allows_distinct_specialists_up_to_portfolio_ceiling():
    ex = PaperPortfolioExecutor()
    for i in range(3):
        assert ex.on_signal(signal(sid=f"REALDNA_{i}"), 2400) is not None
    assert ex.on_signal(signal(sid="REALDNA_3"), 2400) is None
