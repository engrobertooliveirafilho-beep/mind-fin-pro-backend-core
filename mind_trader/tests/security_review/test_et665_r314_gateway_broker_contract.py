"""R314: behavioral gateway rejects PAPER broker responses with unsafe routing metadata."""
from types import SimpleNamespace

import pytest

from mind_trader.app.execution import gateway as gw


@pytest.mark.parametrize("overrides,expected", [
    ({}, "ACCEPT_SIMULATED_ORDER"),
    ({"production": "ENABLED"}, "REJECT_ORDER"),
    ({"production": None}, "REJECT_ORDER"),
    ({"live": "ALLOWED"}, "REJECT_ORDER"),
    ({"live": None}, "REJECT_ORDER"),
    ({"real_broker_routing": "ENABLED"}, "REJECT_ORDER"),
    ({"real_broker_routing": None}, "REJECT_ORDER"),
    ({"fill": {"filled": False}}, "REJECT_ORDER"),
    ({"fill": None}, "REJECT_ORDER"),
    ({"decision": "PAPER_ORDER_REJECTED_FILL"}, "REJECT_ORDER"),
])
def test_r314_gateway_fails_closed_on_broker_metadata(monkeypatch, tmp_path, overrides, expected):
    gateway = gw.ExecutionGateway.__new__(gw.ExecutionGateway)
    gateway.ledger_path = str(tmp_path / "gateway.jsonl")
    gateway.ftmo_audit_path = str(tmp_path / "ftmo.json")
    gateway.paper_broker_ledger_path = str(tmp_path / "broker.jsonl")
    gateway.ftmo_ruleset = {"version": "TEST"}
    gateway.ftmo_config_valid = {"valid": True, "hash": "testhash"}
    gateway.risk = SimpleNamespace(validate=lambda trade: (True, "OK"))
    gateway.ftmo = SimpleNamespace(validate=lambda trade: (True, "OK"))
    gateway.adv = SimpleNamespace(review_trade=lambda *args: {"adversarial_passed": True, "decision": "PASS"})
    gateway.paper = SimpleNamespace(
        ftmo_config_path=str(tmp_path / "ftmo_config.json"),
        pre_trade_check=lambda risk: {"allowed": True, "decision": "ALLOW_PAPER"},
    )

    monkeypatch.setattr(gw, "TradeIntent", lambda **kw: SimpleNamespace(**kw))
    monkeypatch.setattr(gw, "audit_rule_application", lambda *args: {"decision": "ALLOW_FTMO_SIMULATION"})
    monkeypatch.setattr(gw, "require_defined_regime", lambda *args: (True, "OK"))

    broker_response = {
        "decision": "PAPER_ORDER_ACCEPTED",
        "fill": {"filled": True},
        "production": "BLOCKED",
        "live": "FORBIDDEN",
        "real_broker_routing": "DISABLED",
    }
    broker_response.update(overrides)
    calls = []
    def broker_stub(*args, **kwargs):
        calls.append((args, kwargs))
        return broker_response
    monkeypatch.setattr(gw, "paper_route_order", broker_stub)

    trade = {
        "symbol": "EURUSD", "strategy_id": "R314_TEST",
        "entry": 100.0, "stop": 99.0, "target": 102.0,
        "risk_amount": 1.0,
    }
    result = gateway.submit_order("PAPER", trade, {"regime": "TREND"}, {"genome_id": "test"})
    assert len(calls) == 1
    assert result["decision"] == expected
    assert result["production"] == "BLOCKED"
    assert result["real_broker_routing"] == "DISABLED"
    if expected == "REJECT_ORDER":
        assert any(c["layer"] == "PAPER_BROKER" and c["ok"] is False for c in result["checks"])
