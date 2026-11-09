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
    assert accepted["paper_reservation_id"] == token
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


def test_pending_reservation_prevents_session_close(tmp_path):
    g = gateway(tmp_path)
    assert g.submit_order("PAPER", trade(), regime(), genome())["decision"] == "ACCEPT_SIMULATED_ORDER"
    result = g.paper.close_session()
    assert result["decision"] == "BLOCK_CLOSE_PENDING_RESERVATIONS"
    assert g.paper.daily_summary()["status"] == "OPEN"


def test_pending_reservation_prevents_reopen_after_closed_state(tmp_path):
    g = gateway(tmp_path)
    assert g.submit_order("PAPER", trade(), regime(), genome())["decision"] == "ACCEPT_SIMULATED_ORDER"
    path = tmp_path / "session.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["status"] = "CLOSED"
    path.write_text(json.dumps(state), encoding="utf-8")
    assert g.paper.open_session()["decision"] == "BLOCK_SESSION_PENDING_RESERVATIONS"


def test_close_session_fails_closed_when_reservation_lock_exists(tmp_path):
    g = gateway(tmp_path)
    lock = tmp_path / "session.json.reserve.lock"
    lock.write_text("held", encoding="utf-8")
    try:
        result = g.paper.close_session()
        assert result["decision"] == "BLOCK_CLOSE_RESERVATION_LOCKED"
        assert g.paper.daily_summary()["status"] == "OPEN"
    finally:
        lock.unlink()


def test_open_session_fails_closed_when_reservation_lock_exists(tmp_path):
    g = gateway(tmp_path)
    assert g.paper.close_session()["decision"] == "SESSION_CLOSED"
    lock = tmp_path / "session.json.reserve.lock"
    lock.write_text("held", encoding="utf-8")
    try:
        assert g.paper.open_session()["decision"] == "BLOCK_OPEN_RESERVATION_LOCKED"
        assert g.paper.daily_summary()["status"] == "CLOSED"
    finally:
        lock.unlink()


def test_rejected_paper_order_has_no_reservation_id(tmp_path):
    g = gateway(tmp_path)
    bad = trade()
    bad["symbol"] = "INVALID_SYMBOL"
    result = g.submit_order("PAPER", bad, regime(), genome())
    assert result["decision"] != "ACCEPT_SIMULATED_ORDER"
    assert not result.get("paper_reservation_id")


def test_duplicate_reservation_ids_fail_closed(tmp_path):
    g = gateway(tmp_path)
    path = tmp_path / "session.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["pending_paper_orders"] = [{"id":"same","risk":100},{"id":"same","risk":100}]
    path.write_text(json.dumps(state), encoding="utf-8")
    assert g.paper.pre_trade_check(100)["allowed"] is False
    assert g.paper.settle_paper_order("same", -100)["decision"] == "BLOCK_SETTLEMENT_NO_OPEN_SESSION"
    assert json.loads(path.read_text(encoding="utf-8")) == state


def test_oversubscribed_reservation_count_fails_closed(tmp_path):
    g = gateway(tmp_path)
    path = tmp_path / "session.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["trades"] = state["max_daily_trades"] - 1
    state["pending_paper_orders"] = [{"id":"a","risk":100},{"id":"b","risk":100}]
    path.write_text(json.dumps(state), encoding="utf-8")
    assert g.paper.pre_trade_check(100)["allowed"] is False
    assert g.paper.record_trade_result(-100)["decision"] == "BLOCK_RECORD_NO_OPEN_SESSION"
