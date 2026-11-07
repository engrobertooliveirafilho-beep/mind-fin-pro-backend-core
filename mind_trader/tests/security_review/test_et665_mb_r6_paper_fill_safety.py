"""ET665.MB.R6: PAPER fill must reject malformed values and impossible costs."""
import pytest
from mind_trader.app.execution.paper_fill_model import simulate_fill

ORDER={"entry":100.0,"stop":98.0,"target":104.0,"side":"BUY"}

@pytest.mark.parametrize("order", [None, [], {}, "bad", 0])
def test_non_order_payload_never_fills(order):
    assert simulate_fill(order)["filled"] is False

@pytest.mark.parametrize("side", [None, 1, [], "HOLD", "buy", True])
def test_invalid_side_never_fills(side):
    assert simulate_fill({**ORDER,"side":side})["filled"] is False

@pytest.mark.parametrize("field", ["entry","stop","target"])
@pytest.mark.parametrize("bad", [None, True, "100", float("nan"), float("inf"), -1, 0])
def test_invalid_price_fields_never_fill(field, bad):
    assert simulate_fill({**ORDER,field:bad})["filled"] is False

@pytest.mark.parametrize("field", ["spread","slippage","commission"])
@pytest.mark.parametrize("bad", [None, True, "1", float("nan"), float("inf"), -1])
def test_invalid_costs_never_fill(field, bad):
    costs={"spread":0.0,"slippage":0.0,"commission":0.0}
    costs[field]=bad
    assert simulate_fill(ORDER,**costs)["filled"] is False

def test_nonfinite_result_rejected():
    assert simulate_fill(ORDER, spread=1e308, slippage=1e308)["filled"] is False

def test_nonpositive_sell_fill_rejected():
    assert simulate_fill({**ORDER,"side":"SELL"}, spread=200)["filled"] is False

@pytest.mark.parametrize("side", ["BUY","SELL"])
def test_valid_simulation_remains_paper_only(side):
    result=simulate_fill({**ORDER,"side":side}, spread=1.0, slippage=0.2, commission=0.1)
    assert result["filled"] is True
    assert result["decision"]=="FILL_SIMULATED"
    assert result["production"]=="BLOCKED"
    assert result["live"]=="FORBIDDEN"
