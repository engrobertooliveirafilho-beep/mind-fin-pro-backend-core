"""ET665.R342: regression contracts for durable PAPER slot/risk reservations."""
import json
from mind_trader.tests.test_p896_gateway_paper_broker_integration import gateway, trade, regime, genome


def test_second_paper_order_must_not_exceed_one_slot_without_settlement(tmp_path):
    g = gateway(tmp_path)
    session_path = tmp_path / "session.json"
    session = json.loads(session_path.read_text(encoding="utf-8"))
    session["trades"] = session["max_daily_trades"] - 1
    session_path.write_text(json.dumps(session), encoding="utf-8")
    first = g.submit_order("PAPER", trade(), regime(), genome())
    assert first["decision"] == "ACCEPT_SIMULATED_ORDER"
    second = g.submit_order("PAPER", trade(), regime(), genome())
    assert second["decision"] == "BLOCKED_PAPER_SESSION"


def test_second_paper_order_must_respect_outstanding_risk(tmp_path):
    g = gateway(tmp_path)
    session_path = tmp_path / "session.json"
    session = json.loads(session_path.read_text(encoding="utf-8"))
    session["daily_pnl"] = -(session["max_daily_loss"] - 750)
    session_path.write_text(json.dumps(session), encoding="utf-8")
    first = g.submit_order("PAPER", trade(), regime(), genome())
    assert first["decision"] == "ACCEPT_SIMULATED_ORDER"
    second = g.submit_order("PAPER", trade(), regime(), genome())
    assert second["decision"] == "BLOCKED_PAPER_SESSION"
