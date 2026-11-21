from app.runtime.p2071_2080_realtime_paper_runtime import MarketTick, RealtimeFeatureBuilder

def _frame(prices):
    builder = RealtimeFeatureBuilder()
    frame = None
    for i, price in enumerate(prices):
        frame = builder.update(MarketTick(ts=i+1, symbol="XAUUSD", bid=price-0.1, ask=price+0.1, last=price, volume=100))
    return frame

def test_flat_market_rsi_is_neutral():
    assert _frame([2400.0] * 20).rsi_14 == 50.0

def test_rising_market_rsi_reaches_100():
    assert _frame([2400.0 + i for i in range(20)]).rsi_14 == 100.0

def test_falling_market_rsi_reaches_zero():
    assert _frame([2400.0 - i for i in range(20)]).rsi_14 == 0.0
