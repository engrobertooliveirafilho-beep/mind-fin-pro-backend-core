"""ET665.MB.R2: malformed PAPER adapter inputs must fail closed offline."""
import pytest
from mind_trader.app.execution.safe_broker_adapter import broker_adapter_contract, validate_order_payload

@pytest.mark.parametrize("broker", [None, [], {}, 42, "LIVE", "UNKNOWN"])
def test_unknown_or_unhashable_broker_is_blocked(broker):
    result = broker_adapter_contract(broker)
    assert result["decision"] == "BROKER_UNSUPPORTED"
    assert result["production"] == "BLOCKED"

@pytest.mark.parametrize("order", [None, [], (), 0, "not_an_order", True])
def test_malformed_order_type_is_rejected(order):
    result = validate_order_payload(order)
    assert result["valid"] is False
    assert result["decision"] == "ORDER_PAYLOAD_INVALID"

@pytest.mark.parametrize("field", ["symbol", "side", "entry", "stop", "target", "risk_amount", "strategy_id"])
def test_missing_required_order_field_is_rejected(field):
    order = dict(symbol="EURUSD", side="BUY", entry=1.1, stop=1.0, target=1.2, risk_amount=1.0, strategy_id="PAPER_TEST")
    del order[field]
    result = validate_order_payload(order)
    assert result["valid"] is False
    assert field in result["missing"]

def test_valid_paper_order_structure_remains_accepted():
    order = dict(symbol="EURUSD", side="BUY", entry=1.1, stop=1.0, target=1.2, risk_amount=1.0, strategy_id="PAPER_TEST")
    assert validate_order_payload(order)["valid"] is True
