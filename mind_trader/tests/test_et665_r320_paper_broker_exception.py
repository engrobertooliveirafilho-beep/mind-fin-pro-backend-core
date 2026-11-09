"""R320: fail-closed PAPER broker failure; offline only."""
import json
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
    events = [json.loads(line) for line in (tmp_path / "exec.jsonl").read_text(encoding="utf-8").splitlines()]
    assert events[-1]["decision"] == "REJECT_ORDER"
    assert events[-1]["paper_broker"]["decision"] == "PAPER_BROKER_EXCEPTION"
    assert any(c["reason"] == "PAPER_BROKER_EXCEPTION" for c in events[-1]["checks"])


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


def test_closed_paper_session_never_invokes_broker(tmp_path):
    g = gateway(tmp_path)
    g.paper.close_session()
    with patch("mind_trader.app.execution.gateway.paper_route_order") as broker:
        result = g.submit_order("PAPER", trade(), regime(), genome())
    broker.assert_not_called()
    assert result["decision"] == "BLOCKED_PAPER_SESSION"
    assert result["production"] == "BLOCKED"


def test_live_mode_never_invokes_paper_broker(tmp_path):
    g = gateway(tmp_path)
    with patch("mind_trader.app.execution.gateway.paper_route_order") as broker:
        result = g.submit_order("LIVE", trade(), regime(), genome())
    broker.assert_not_called()
    assert result["decision"] == "FORCE_BLOCK_LIVE_OR_PRODUCTION"
    assert result["production"] == "BLOCKED"


def test_broker_real_routing_claim_must_reject(tmp_path):
    g = gateway(tmp_path)
    broker_reply = {"decision": "PAPER_ORDER_ACCEPTED", "fill": {"filled": True},
                    "production": "BLOCKED", "live": "FORBIDDEN",
                    "real_broker_routing": "ENABLED"}
    with patch("mind_trader.app.execution.gateway.paper_route_order", return_value=broker_reply):
        result = g.submit_order("PAPER", trade(), regime(), genome())
    assert result["decision"] == "REJECT_ORDER"
    assert result["real_broker_routing"] == "DISABLED"
    assert any(c["layer"] == "PAPER_BROKER" and c["ok"] is False for c in result["checks"])


def test_broker_live_flag_must_reject(tmp_path):
    g = gateway(tmp_path)
    broker_reply = {"decision": "PAPER_ORDER_ACCEPTED", "fill": {"filled": True},
                    "production": "BLOCKED", "live": "ENABLED",
                    "real_broker_routing": "DISABLED"}
    with patch("mind_trader.app.execution.gateway.paper_route_order", return_value=broker_reply):
        result = g.submit_order("PAPER", trade(), regime(), genome())
    assert result["decision"] == "REJECT_ORDER"
    assert result["production"] == "BLOCKED"
    assert any(c["layer"] == "PAPER_BROKER" and c["ok"] is False for c in result["checks"])


def test_paper_session_config_drift_never_invokes_broker(tmp_path):
    g = gateway(tmp_path)
    session = json.loads((tmp_path / "session.json").read_text(encoding="utf-8"))
    session["ftmo_config_hash"] = "invalid-offline-hash"
    (tmp_path / "session.json").write_text(json.dumps(session), encoding="utf-8")
    with patch("mind_trader.app.execution.gateway.paper_route_order") as broker:
        result = g.submit_order("PAPER", trade(), regime(), genome())
    broker.assert_not_called()
    assert result["decision"] == "BLOCKED_PAPER_SESSION"
    assert result["session_check"]["decision"] == "BLOCK_PAPER_SESSION_FTMO_CONFIG_DRIFT"
    assert result["production"] == "BLOCKED"


def test_paper_daily_loss_limit_never_invokes_broker(tmp_path):
    g = gateway(tmp_path)
    order = trade()
    order["risk_amount"] = 6000
    with patch("mind_trader.app.execution.gateway.paper_route_order") as broker:
        result = g.submit_order("PAPER", order, regime(), genome())
    broker.assert_not_called()
    assert result["decision"] == "BLOCKED_PAPER_SESSION"
    assert result["session_check"]["decision"] == "BLOCK_DAILY_LOSS_LIMIT"
    assert result["production"] == "BLOCKED"


def test_paper_corrupt_session_never_invokes_broker(tmp_path):
    g = gateway(tmp_path)
    (tmp_path / "session.json").write_text("{invalid-json", encoding="utf-8")
    with patch("mind_trader.app.execution.gateway.paper_route_order") as broker:
        result = g.submit_order("PAPER", trade(), regime(), genome())
    broker.assert_not_called()
    assert result["decision"] == "BLOCKED_PAPER_SESSION"
    assert result["session_check"]["decision"] == "BLOCK_NO_SESSION"
    assert result["production"] == "BLOCKED"


def test_paper_max_daily_trades_never_invokes_broker(tmp_path):
    g = gateway(tmp_path)
    session_path = tmp_path / "session.json"
    session = json.loads(session_path.read_text(encoding="utf-8"))
    session["trades"] = session["max_daily_trades"]
    session_path.write_text(json.dumps(session), encoding="utf-8")
    with patch("mind_trader.app.execution.gateway.paper_route_order") as broker:
        result = g.submit_order("PAPER", trade(), regime(), genome())
    broker.assert_not_called()
    assert result["decision"] == "BLOCKED_PAPER_SESSION"
    assert result["session_check"]["decision"] == "BLOCK_MAX_DAILY_TRADES"
    assert result["production"] == "BLOCKED"


def test_tampered_paper_trade_limit_never_invokes_broker(tmp_path):
    g = gateway(tmp_path)
    path = tmp_path / "session.json"
    session = json.loads(path.read_text(encoding="utf-8"))
    session["max_daily_trades"] += 1000
    path.write_text(json.dumps(session), encoding="utf-8")
    with patch("mind_trader.app.execution.gateway.paper_route_order") as broker:
        result = g.submit_order("PAPER", trade(), regime(), genome())
    broker.assert_not_called()
    assert result["session_check"]["decision"] == "BLOCK_PAPER_SESSION_LIMIT_TAMPERING"
    assert result["production"] == "BLOCKED"


def test_tampered_paper_loss_limit_never_invokes_broker(tmp_path):
    g = gateway(tmp_path)
    path = tmp_path / "session.json"
    session = json.loads(path.read_text(encoding="utf-8"))
    session["max_daily_loss"] *= 100
    path.write_text(json.dumps(session), encoding="utf-8")
    with patch("mind_trader.app.execution.gateway.paper_route_order") as broker:
        result = g.submit_order("PAPER", trade(), regime(), genome())
    broker.assert_not_called()
    assert result["session_check"]["decision"] == "BLOCK_PAPER_SESSION_LIMIT_TAMPERING"
    assert result["production"] == "BLOCKED"
