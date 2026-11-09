"""ET665.R344: reservation settlement is idempotent and risk accounting is durable."""
import json
from mind_trader.tests.test_p896_gateway_paper_broker_integration import gateway, trade, regime, genome


def test_settle_reserved_fill_once(tmp_path):
    g = gateway(tmp_path)
    accepted = g.submit_order("PAPER", trade(), regime(), genome())
    assert accepted["decision"] == "ACCEPT_SIMULATED_ORDER"
    pending = json.loads((tmp_path / "session.json").read_text(encoding="utf-8"))["pending_paper_orders"]
    assert len(pending) == 1
    token = pending[0]["id"]
    result = g.paper.settle_paper_order(token, -100)
    assert result["decision"] == "PAPER_RESERVATION_SETTLED"
    assert result["session"]["trades"] == 1
    assert result["session"]["daily_pnl"] == -100
    assert result["session"]["pending_paper_orders"] == []
    duplicate = g.paper.settle_paper_order(token, -100)
    assert duplicate["decision"] == "BLOCK_SETTLEMENT_UNKNOWN_OR_DUPLICATE_ID"
    assert g.paper.daily_summary()["trades"] == 1


def test_unknown_reservation_never_changes_accounting(tmp_path):
    g = gateway(tmp_path)
    before = (tmp_path / "session.json").read_bytes()
    assert g.paper.settle_paper_order("unknown", -100)["decision"] == "BLOCK_SETTLEMENT_UNKNOWN_OR_DUPLICATE_ID"
    assert (tmp_path / "session.json").read_bytes() == before
