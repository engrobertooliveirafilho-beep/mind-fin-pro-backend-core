"""ET665.R330: documented concurrency/reservation gap, not certification.

This is an expected-failure safety contract: it must not be counted as PASS.
The gateway checks historical trade results, but does not reserve a slot
before sending another simulated order.
"""
import json
import pytest
from mind_trader.tests.test_p896_gateway_paper_broker_integration import gateway, trade, regime, genome


@pytest.mark.xfail(strict=True, reason="ET665.R330: no atomic PAPER order-slot reservation")
def test_second_paper_order_must_not_exceed_one_slot_without_settlement(tmp_path):
    g = gateway(tmp_path)
    session_path = tmp_path / "session.json"
    session = json.loads(session_path.read_text(encoding="utf-8"))
    session["max_daily_trades"] = 1
    session_path.write_text(json.dumps(session), encoding="utf-8")
    first = g.submit_order("PAPER", trade(), regime(), genome())
    assert first["decision"] == "ACCEPT_SIMULATED_ORDER"
    second = g.submit_order("PAPER", trade(), regime(), genome())
    assert second["decision"] == "BLOCKED_PAPER_SESSION"


@pytest.mark.xfail(strict=True, reason="ET665.R331: outstanding PAPER risk is not reserved atomically")
def test_second_paper_order_must_respect_outstanding_risk(tmp_path):
    g = gateway(tmp_path)
    session_path = tmp_path / "session.json"
    session = json.loads(session_path.read_text(encoding="utf-8"))
    session["max_daily_loss"] = 600
    session_path.write_text(json.dumps(session), encoding="utf-8")
    first = g.submit_order("PAPER", trade(), regime(), genome())
    assert first["decision"] == "ACCEPT_SIMULATED_ORDER"
    second = g.submit_order("PAPER", trade(), regime(), genome())
    assert second["decision"] == "BLOCKED_PAPER_SESSION"
