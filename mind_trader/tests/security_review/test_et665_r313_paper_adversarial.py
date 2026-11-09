"""R313: behavioral PAPER broker adversarial checks; no real broker, network, or production."""
import json

import pytest

from mind_trader.app.execution import paper_broker_adapter as broker


def _order():
    return {
        "symbol": "EURUSD", "side": "BUY", "entry": 100.0,
        "stop": 99.0, "target": 102.0, "risk_amount": 1.0,
        "strategy_id": "R313_OFFLINE",
    }


def test_r313_valid_paper_order_has_simulated_fill_and_no_live_route(tmp_path):
    ledger = tmp_path / "paper.jsonl"
    result = broker.paper_route_order(_order(), ledger_path=str(ledger))
    assert result["decision"] == "PAPER_ORDER_ACCEPTED"
    assert result["fill"]["filled"] is True
    assert result["order_status"] == "PAPER_FILLED_SIMULATED"
    assert result["real_broker_routing"] == "DISABLED"
    assert result["production"] == "BLOCKED"
    assert result["live"] == "FORBIDDEN"
    assert json.loads(ledger.read_text().splitlines()[0])["decision"] == result["decision"]


@pytest.mark.parametrize("invalid", [
    {"symbol": "EURUSD"},
    {**_order(), "side": "INVALID"},
    {**_order(), "entry": float("nan")},
    {**_order(), "entry": -1.0},
])
def test_r313_invalid_order_never_accepted(tmp_path, invalid):
    result = broker.paper_route_order(invalid, ledger_path=str(tmp_path / "paper.jsonl"))
    assert result["decision"] != "PAPER_ORDER_ACCEPTED"
    assert result["production"] == "BLOCKED"
    assert result["live"] == "FORBIDDEN"


def test_r313_invalid_ftmo_cost_config_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(broker, "load_ftmo_config", lambda _: (None, {"valid": False}))
    result = broker.paper_route_order(
        _order(), ledger_path=str(tmp_path / "paper.jsonl"),
        ftmo_config_path=str(tmp_path / "bad.json"),
    )
    assert result["decision"] == "PAPER_ORDER_REJECTED_INVALID_COST_CONFIG"
    assert result["production"] == "BLOCKED"


def test_r313_unfillable_order_fails_closed(tmp_path):
    result = broker.paper_route_order(
        _order(), ledger_path=str(tmp_path / "paper.jsonl"),
        spread=250.0,
    )
    assert result["decision"] == "PAPER_ORDER_REJECTED_FILL"
    assert result["fill"]["filled"] is False
    assert result["production"] == "BLOCKED"


def test_r313_network_socket_creation_not_required(tmp_path, monkeypatch):
    import socket

    def denied(*args, **kwargs):
        raise AssertionError("NETWORK_ATTEMPT_FORBIDDEN")

    monkeypatch.setattr(socket, "socket", denied)
    result = broker.paper_route_order(_order(), ledger_path=str(tmp_path / "paper.jsonl"))
    assert result["decision"] == "PAPER_ORDER_ACCEPTED"
    assert result["fill"]["filled"] is True
