import math
from app.runtime.p2071_2080_realtime_paper_runtime import (
    PaperPortfolioExecutor, PaperSignal, PaperPosition, FeatureFrame, run_p2071_2080
)

def _signal(side="BUY", confidence=0.9):
    return PaperSignal(ts=1, symbol="XAUUSD", specialist_id="XAUUSD_M1_REALDNA_0004", side=side, confidence=confidence, reason="TEST")

def _frame(mid=101.0):
    return FeatureFrame(ts=2, symbol="XAUUSD", mid=mid, spread=0.2, return_1=0, volatility_20=0, body_to_range=0, rsi_14=50, stoch_14=50, close_position=0.5)

def test_p2067_micro_size_ceiling():
    ex = PaperPortfolioExecutor()
    p = ex.on_signal(_signal(), 100)
    assert p is not None and p.qty == 0.01

def test_unrealized_pnl_is_quantity_weighted():
    ex = PaperPortfolioExecutor()
    ex.on_signal(_signal(), 100)
    assert abs(ex.unrealized_pnl(101) - 0.01) < 1e-10

def test_realized_pnl_is_quantity_weighted():
    ex = PaperPortfolioExecutor()
    ex.on_signal(_signal(), 100)
    ex.mark_to_market(_frame(106))
    assert not ex.positions
    assert abs(ex.equity - 100000.06) < 1e-7
    assert abs(ex.closed[0]["pnl"] - 0.06) < 1e-10

def test_invalid_side_cannot_open_position():
    ex = PaperPortfolioExecutor()
    assert ex.on_signal(_signal("HOLD"), 100) is None
    assert ex.on_signal(_signal("UNKNOWN"), 100) is None
    assert not ex.positions

def test_nonfinite_prices_and_confidence_rejected():
    ex = PaperPortfolioExecutor()
    for price in [float("nan"), float("inf"), 0, -1]:
        assert ex.on_signal(_signal(), price) is None
    for confidence in [float("nan"), float("inf"), -1]:
        assert ex.on_signal(_signal(confidence=confidence), 100) is None

def test_original_portfolio_risk_certification_is_not_promoted(tmp_path):
    path = "data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json"
    result = run_p2071_2080(path, str(tmp_path), cycles=5)
    assert result["status"] == "FAIL"
    assert result["mission_status"]["P2074_PAPER_PORTFOLIO_EXECUTOR"] == "PENDING_RISK_AND_FILL_VALIDATION"
    assert result["mission_status"]["P2080_REALTIME_RUNTIME_CERTIFICATION"] == "FAIL"
    assert result["realtime_feed_certified"] is False
