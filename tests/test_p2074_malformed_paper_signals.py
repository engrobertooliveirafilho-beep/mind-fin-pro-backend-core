from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperSignal

def _signal(**kwargs):
    payload = dict(ts=100, symbol="XAUUSD", specialist_id="XAUUSD_M1_REALDNA_0004", side="BUY", confidence=0.9, reason="OFFLINE_TEST")
    payload.update(kwargs)
    return PaperSignal(**payload)

def test_reject_non_numeric_price_without_exception():
    ex = PaperPortfolioExecutor()
    for price in (None, "2400", True, [], {}):
        assert ex.on_signal(_signal(), price) is None

def test_reject_non_numeric_confidence_without_exception():
    ex = PaperPortfolioExecutor()
    for confidence in (None, "0.9", True, [], {}):
        assert ex.on_signal(_signal(confidence=confidence), 2400) is None

def test_reject_confidence_above_one():
    assert PaperPortfolioExecutor().on_signal(_signal(confidence=1.01), 2400) is None

def test_reject_wrong_symbol_and_blank_specialist():
    ex = PaperPortfolioExecutor()
    assert ex.on_signal(_signal(symbol="EURUSD"), 2400) is None
    assert ex.on_signal(_signal(specialist_id="  "), 2400) is None

def test_valid_xauusd_paper_signal_still_opens():
    ex = PaperPortfolioExecutor()
    pos = ex.on_signal(_signal(), 2400)
    assert pos is not None and pos.qty == 0.01
