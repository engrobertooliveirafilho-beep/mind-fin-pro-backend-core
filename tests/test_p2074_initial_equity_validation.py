import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor

@pytest.mark.parametrize("value", [0, -1, True, None, "100000", float("nan"), float("inf"), -float("inf")])
def test_invalid_initial_equity_fails_closed(value):
    with pytest.raises(ValueError, match="INVALID_PAPER_INITIAL_EQUITY"):
        PaperPortfolioExecutor(initial_equity=value)

def test_valid_initial_equity_preserved():
    executor = PaperPortfolioExecutor(initial_equity=100000.0)
    assert executor.equity == 100000.0
    assert executor.initial_equity == 100000.0
