"""R320: fail-closed PAPER broker failure; offline only."""
from unittest.mock import patch
from mind_trader.tests.test_p896_gateway_paper_broker_integration import gateway, trade, regime, genome


def test_paper_broker_exception_must_reject_without_simulated_acceptance(tmp_path):
    g = gateway(tmp_path)
    with patch("mind_trader.app.execution.gateway.paper_route_order", side_effect=RuntimeError("offline injected broker failure")):
        result = g.submit_order("PAPER", trade(), regime(), genome())
    assert result["decision"] == "REJECT_ORDER"
    assert result["production"] == "BLOCKED"
    assert result["real_broker_routing"] == "DISABLED"
    assert result["order_status"] == "SIMULATED_REJECTED"
    assert any(c["layer"] == "PAPER_BROKER" and c["ok"] is False for c in result["checks"])


def test_paper_broker_malformed_response_must_reject(tmp_path):
    g = gateway(tmp_path)
    with patch("mind_trader.app.execution.gateway.paper_route_order", return_value=None):
        result = g.submit_order("PAPER", trade(), regime(), genome())
    assert result["decision"] == "REJECT_ORDER"
    assert result["production"] == "BLOCKED"
    assert result["real_broker_routing"] == "DISABLED"
    assert any(c["layer"] == "PAPER_BROKER" and c["ok"] is False for c in result["checks"])


def test_paper_broker_claimed_acceptance_without_fill_must_reject(tmp_path):
    g = gateway(tmp_path)
    broker_reply = {"decision": "PAPER_ORDER_ACCEPTED", "fill": {"filled": False},
                    "production": "BLOCKED", "live": "FORBIDDEN",
                    "real_broker_routing": "DISABLED"}
    with patch("mind_trader.app.execution.gateway.paper_route_order", return_value=broker_reply):
        result = g.submit_order("PAPER", trade(), regime(), genome())
    assert result["decision"] == "REJECT_ORDER"
    assert result["order_status"] == "SIMULATED_REJECTED"
    assert result["production"] == "BLOCKED"
    assert result["real_broker_routing"] == "DISABLED"
    assert any(c["layer"] == "PAPER_BROKER" and c["ok"] is False for c in result["checks"])
