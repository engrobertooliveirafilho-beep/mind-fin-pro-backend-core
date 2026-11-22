import math
import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperSignal, FeatureFrame

def _frame(symbol="XAUUSD", mid=100.0, spread=0.2):
    return FeatureFrame(ts=2, symbol=symbol, mid=mid, spread=spread, return_1=0, volatility_20=0, body_to_range=0, rsi_14=50, stoch_14=50, close_position=0.5)

@pytest.mark.parametrize("symbol", ["EURUSD", "", None])
def test_cross_symbol_mark_rejected_without_state_mutation(symbol):
    ex = PaperPortfolioExecutor()
    pos = ex.on_signal(PaperSignal(ts=1, symbol="XAUUSD", specialist_id="test", side="BUY", confidence=0.9, reason="test"), 100)
    assert pos is not None
    before = (ex.equity, len(ex.positions), len(ex.closed), ex._peak_equity)
    with pytest.raises(ValueError, match="INVALID_PAPER_MARK_SYMBOL"):
        ex.mark_to_market(_frame(symbol=symbol, mid=200))
    assert before == (ex.equity, len(ex.positions), len(ex.closed), ex._peak_equity)

@pytest.mark.parametrize("spread", [float("nan"), float("inf"), -0.1, "bad", True])
def test_invalid_spread_rejected_without_risk_state_mutation(spread):
    ex = PaperPortfolioExecutor()
    before = (ex.equity, ex._peak_equity, ex._risk_locked)
    with pytest.raises(ValueError, match="INVALID_PAPER_MARK_SPREAD"):
        ex.mark_to_market(_frame(spread=spread))
    assert before == (ex.equity, ex._peak_equity, ex._risk_locked)

@pytest.mark.parametrize("mid", ["bad", None, True, float("nan")])
def test_invalid_mid_rejected_without_type_error(mid):
    ex = PaperPortfolioExecutor()
    with pytest.raises(ValueError, match="INVALID_PAPER_MARK_PRICE"):
        ex.mark_to_market(_frame(mid=mid))
