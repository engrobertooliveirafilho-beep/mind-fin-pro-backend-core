import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import RealtimeFeatureBuilder, MarketTick

def _tick(ts=100, symbol="XAUUSD", bid=100.0, ask=100.2, last=100.1, volume=10.0):
    return MarketTick(ts=ts, symbol=symbol, bid=bid, ask=ask, last=last, volume=volume)

@pytest.mark.parametrize("kwargs,reason", [
    ({"symbol":"EURUSD"}, "INVALID_PAPER_FEED_IDENTITY"),
    ({"ts":True}, "INVALID_PAPER_FEED_IDENTITY"),
    ({"bid":float("nan")}, "INVALID_PAPER_FEED_VALUE"),
    ({"ask":"bad"}, "INVALID_PAPER_FEED_VALUE"),
    ({"ask":99.0}, "INVALID_PAPER_FEED_QUOTE"),
    ({"bid":0}, "INVALID_PAPER_FEED_QUOTE"),
    ({"volume":-1}, "INVALID_PAPER_FEED_QUOTE"),
])
def test_invalid_quote_does_not_pollute_feature_history(kwargs, reason):
    builder = RealtimeFeatureBuilder()
    with pytest.raises(ValueError, match=reason):
        builder.update(_tick(**kwargs))
    assert builder.history == []

def test_retroactive_feed_rejected_without_history_mutation():
    builder = RealtimeFeatureBuilder()
    builder.update(_tick(100))
    with pytest.raises(ValueError, match="OUT_OF_ORDER_PAPER_FEED"):
        builder.update(_tick(99))
    assert len(builder.history) == 1

def test_duplicate_feed_timestamp_rejected():
    builder = RealtimeFeatureBuilder()
    builder.update(_tick(100))
    with pytest.raises(ValueError, match="OUT_OF_ORDER_PAPER_FEED"):
        builder.update(_tick(100))
    assert len(builder.history) == 1

def test_next_valid_quote_builds_features():
    builder = RealtimeFeatureBuilder()
    builder.update(_tick(100))
    frame = builder.update(_tick(101))
    assert frame.symbol == "XAUUSD"
    assert len(builder.history) == 2
