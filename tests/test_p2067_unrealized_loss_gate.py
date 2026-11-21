from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperPosition, PaperSignal

def _signal(sid="SECOND"):
    return PaperSignal(ts=100, symbol="XAUUSD", specialist_id=sid, side="BUY", confidence=0.9, reason="TEST")

def _open_loss(ex, entry, qty):
    ex.positions["EXISTING"] = PaperPosition(position_id="EXISTING", symbol="XAUUSD", specialist_id="FIRST", side="BUY", entry=entry, sl=entry-10000, tp=entry+10000, qty=qty, open_ts=1)

def test_unrealized_daily_loss_prevents_new_entry():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    _open_loss(ex, 2000, 1.0)
    assert ex.on_signal(_signal(), 900) is None
    assert len(ex.positions) == 1

def test_unrealized_total_loss_prevents_new_entry():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    _open_loss(ex, 5000, 1.0)
    assert ex.on_signal(_signal(), 1900) is None
    assert len(ex.positions) == 1

def test_unrealized_profit_does_not_disable_daily_gate():
    ex = PaperPortfolioExecutor(initial_equity=100000)
    _open_loss(ex, 2000, 0.01)
    assert ex.on_signal(_signal(), 2100) is not None

def test_unrealized_pnl_preserves_position_quantity():
    ex = PaperPortfolioExecutor()
    _open_loss(ex, 2000, 0.01)
    assert abs(ex.current_equity(1900) - 99999.0) < 1e-9
