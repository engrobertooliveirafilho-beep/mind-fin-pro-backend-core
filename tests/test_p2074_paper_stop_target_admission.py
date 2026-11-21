import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperSignal

@pytest.mark.parametrize("side,price", [
    ("BUY", 0.1), ("BUY", 3.0), ("SELL", 0.1), ("SELL", 6.0),
])
def test_unrepresentable_paper_stop_or_target_rejected_without_sequence(side, price):
    executor = PaperPortfolioExecutor()
    signal = PaperSignal(ts=100, symbol="XAUUSD", specialist_id="S1", side=side, confidence=0.9, reason="TEST")
    assert executor.on_signal(signal, price) is None
    assert executor.seq == 0
    assert executor.positions == {}

@pytest.mark.parametrize("side,price", [("BUY", 4.0), ("SELL", 7.0)])
def test_representable_low_price_paper_trade_still_allowed(side, price):
    executor = PaperPortfolioExecutor()
    signal = PaperSignal(ts=100, symbol="XAUUSD", specialist_id="S1", side=side, confidence=0.9, reason="TEST")
    assert executor.on_signal(signal, price) is not None
    assert executor.seq == 1
