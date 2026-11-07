"""ET665.BW: malformed inputs must fail closed and be recorded before other services run."""
import json
import pytest
from mind_trader.app.execution.gateway import ExecutionGateway

@pytest.mark.parametrize("mode,trade,regime,genome,expected", [
    ([], {}, {}, {}, "BLOCKED_INVALID_EXECUTION_MODE_TYPE"),
    ({}, {}, {}, {}, "BLOCKED_INVALID_EXECUTION_MODE_TYPE"),
    (None, {}, {}, {}, "BLOCKED_INVALID_EXECUTION_MODE_TYPE"),
    ("PAPER", None, {}, {}, "BLOCKED_INVALID_ORDER_INPUT_TYPE"),
    ("PAPER", {}, [], {}, "BLOCKED_INVALID_ORDER_INPUT_TYPE"),
    ("PAPER", {}, {}, None, "BLOCKED_INVALID_ORDER_INPUT_TYPE"),
    ("LIVE", None, {}, {}, "BLOCKED_INVALID_ORDER_INPUT_TYPE"),
])
def test_gateway_malformed_types_write_blocked_ledger(tmp_path, mode, trade, regime, genome, expected):
    gateway = ExecutionGateway.__new__(ExecutionGateway)
    gateway.ledger_path = str(tmp_path / "execution.jsonl")
    result = gateway.submit_order(mode, trade, regime, genome)
    assert result["decision"] == expected
    assert result["production"] == "BLOCKED"
    assert result["edge_claim"] == "NONE"
    events = [json.loads(line) for line in (tmp_path / "execution.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(events) == 1
    assert events[0]["decision"] == expected
    assert events[0]["production"] == "BLOCKED"
    assert "trade" not in events[0]
