import math
import pytest
from app.runtime.p2081_2090_realtime_portfolio_governance import extract_runtime_metrics


def baseline():
    return {"metrics": {
        "cycles": 1000, "frames_built": 1000, "signals_generated": 30,
        "closed_trades": 12, "open_positions": 0, "initial_equity": 100000.,
        "final_mark_to_market_equity": 100500., "paper_mark_to_market_pnl": 500.,
        "drawdown_pct": -0.01, "drawdown_abs": -1000., "peak_equity": 101000.,
        "trough_equity": 99000.,
    }}


def test_valid_paper_metrics():
    assert extract_runtime_metrics(baseline())["cycles"] == 1000


@pytest.mark.parametrize("key,value,error", [
    ("cycles", 1000.9, "P2071_RUNTIME_COUNTER_INVALID"),
    ("cycles", -1, "P2071_RUNTIME_COUNTER_INVALID"),
    ("closed_trades", True, "P2071_RUNTIME_METRIC_INVALID"),
    ("paper_mark_to_market_pnl", float("nan"), "P2071_RUNTIME_METRIC_INVALID"),
    ("final_mark_to_market_equity", float("inf"), "P2071_RUNTIME_METRIC_INVALID"),
    ("initial_equity", 0, "P2071_RUNTIME_EQUITY_INVALID"),
    ("drawdown_abs", 1, "P2071_RUNTIME_DRAWDOWN_INVALID"),
])
def test_invalid_paper_metrics_rejected(key, value, error):
    payload = baseline()
    payload["metrics"][key] = value
    with pytest.raises(ValueError, match=error):
        extract_runtime_metrics(payload)

def test_signed_drawdown_from_original_p2071_is_preserved():
    payload = baseline()
    payload["metrics"]["drawdown_abs"] = -953.05314
    payload["metrics"]["drawdown_pct"] = -0.00953053
    actual = extract_runtime_metrics(payload)
    assert actual["drawdown_abs"] == -953.05314
    assert actual["drawdown_pct"] == -0.00953053
