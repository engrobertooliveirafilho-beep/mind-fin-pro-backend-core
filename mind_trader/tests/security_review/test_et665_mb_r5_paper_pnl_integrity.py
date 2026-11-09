"""ET665.MB.R5 — offline PAPER PnL integrity regressions."""
import json
import pytest
from mind_trader.app.execution.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

@pytest.fixture
def session(tmp_path):
    cfg=tmp_path/"ftmo.json"
    save_default_ftmo_config(str(cfg))
    manager=PaperTradingSessionManager(str(tmp_path/"session.json"), str(tmp_path/"ledger.jsonl"), str(cfg))
    assert manager.open_session()["decision"]=="SESSION_OPENED"
    return manager

@pytest.mark.parametrize("pnl", [None, [], {}, "100", True, False, float("nan"), float("inf"), float("-inf")])
def test_invalid_pnl_does_not_mutate_session_or_ledger(session, pnl):
    before=session.session_path.read_bytes()
    ledger_before=session.ledger_path.read_bytes()
    result=session.record_trade_result(pnl)
    assert result["decision"]=="BLOCK_RECORD_INVALID_PNL"
    assert session.session_path.read_bytes()==before
    assert session.ledger_path.read_bytes()==ledger_before

@pytest.mark.parametrize("pnl,expected_streak", [(-25.0, 1), (12.5, 0), (0.0, 0)])
def test_finite_pnl_updates_paper_only(session, pnl, expected_streak):
    result=session.record_trade_result(pnl)
    assert result["decision"]=="TRADE_RECORDED"
    assert result["production"]=="BLOCKED"
    assert result["session"]["trades"]==1
    assert result["session"]["daily_pnl"]==pnl
    assert result["session"]["loss_streak"]==expected_streak

def test_overflowing_finite_pnl_is_rejected_without_mutation(session):
    data=json.loads(session.session_path.read_text(encoding="utf-8"))
    data["daily_pnl"]=1e308
    session.session_path.write_text(json.dumps(data), encoding="utf-8")
    before=session.session_path.read_bytes()
    ledger_before=session.ledger_path.read_bytes()
    assert session.record_trade_result(1e308)["decision"]=="BLOCK_RECORD_INVALID_PNL"
    assert session.session_path.read_bytes()==before
    assert session.ledger_path.read_bytes()==ledger_before

def test_closed_session_cannot_record_finite_pnl(session):
    assert session.close_session()["decision"]=="SESSION_CLOSED"
    assert session.record_trade_result(10)["decision"]=="BLOCK_RECORD_NO_OPEN_SESSION"
