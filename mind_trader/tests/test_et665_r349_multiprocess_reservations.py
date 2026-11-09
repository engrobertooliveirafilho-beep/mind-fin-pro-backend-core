"""ET665.R349: real multi-process PAPER reservation adversarial regressions (offline)."""
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from mind_trader.tests.test_p896_gateway_paper_broker_integration import gateway
from mind_trader.app.execution.paper_session import PaperTradingSessionManager


def _reserve(paths):
    session, ledger, config, risk = paths
    manager = PaperTradingSessionManager(session, ledger, config)
    return manager.reserve_paper_order(risk)


def test_multiprocess_reservations_never_oversubscribe_trade_slots(tmp_path):
    g = gateway(tmp_path)
    path = tmp_path / "session.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["trades"] = state["max_daily_trades"] - 1
    path.write_text(json.dumps(state), encoding="utf-8")
    args = (str(path), str(tmp_path / "day.jsonl"), str(tmp_path / "ftmo.json"), 100)
    with ProcessPoolExecutor(max_workers=6, mp_context=multiprocessing.get_context("spawn")) as pool:
        results = list(pool.map(_reserve, [args] * 6))
    assert sum(x["allowed"] for x in results) == 1
    final = json.loads(path.read_text(encoding="utf-8"))
    assert final["trades"] + len(final["pending_paper_orders"]) <= final["max_daily_trades"]


def test_multiprocess_reservations_never_oversubscribe_daily_risk(tmp_path):
    g = gateway(tmp_path)
    path = tmp_path / "session.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["daily_pnl"] = -(state["max_daily_loss"] - 750)
    path.write_text(json.dumps(state), encoding="utf-8")
    args = (str(path), str(tmp_path / "day.jsonl"), str(tmp_path / "ftmo.json"), 500)
    with ProcessPoolExecutor(max_workers=6, mp_context=multiprocessing.get_context("spawn")) as pool:
        results = list(pool.map(_reserve, [args] * 6))
    assert sum(x["allowed"] for x in results) == 1
    final = json.loads(path.read_text(encoding="utf-8"))
    assert max(0, -final["daily_pnl"]) + sum(x["risk"] for x in final["pending_paper_orders"]) <= final["max_daily_loss"]


def test_legacy_result_blocked_when_reservation_lock_held(tmp_path):
    g = gateway(tmp_path)
    lock = tmp_path / "session.json.reserve.lock"
    before = (tmp_path / "session.json").read_bytes()
    lock.write_text("held", encoding="utf-8")
    try:
        assert g.paper.record_trade_result(-100)["decision"] == "BLOCK_RECORD_RESERVATION_LOCKED"
        assert (tmp_path / "session.json").read_bytes() == before
    finally:
        lock.unlink()
