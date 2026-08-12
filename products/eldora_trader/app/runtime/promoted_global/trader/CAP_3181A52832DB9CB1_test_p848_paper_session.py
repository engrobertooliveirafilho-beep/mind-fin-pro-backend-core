from pathlib import Path
from mind_trader.app.execution.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

def mgr(tmp_path):
    cfg=tmp_path/"ftmo.json"; save_default_ftmo_config(str(cfg))
    return PaperTradingSessionManager(str(tmp_path/"session.json"),str(tmp_path/"ledger.jsonl"),str(cfg))

def test_open_session_requires_valid_config(tmp_path):
    m=PaperTradingSessionManager(str(tmp_path/"s.json"),str(tmp_path/"l.jsonl"),str(tmp_path/"missing.json"))
    r=m.open_session()
    assert r["decision"]=="BLOCK_SESSION_INVALID_FTMO_CONFIG"

def test_open_and_close_session(tmp_path):
    m=mgr(tmp_path)
    assert m.open_session()["decision"]=="SESSION_OPENED"
    assert m.close_session()["decision"]=="SESSION_CLOSED"

def test_pre_trade_blocks_without_session(tmp_path):
    m=mgr(tmp_path)
    r=m.pre_trade_check(100)
    assert r["decision"]=="BLOCK_NO_SESSION"

def test_pre_trade_allows_open_session(tmp_path):
    m=mgr(tmp_path)
    m.open_session()
    r=m.pre_trade_check(100)
    assert r["allowed"] is True
    assert r["decision"]=="ALLOW_PAPER_TRADE"

def test_trade_result_updates_summary(tmp_path):
    m=mgr(tmp_path)
    m.open_session()
    m.record_trade_result(-50)
    s=m.daily_summary()
    assert s["daily_pnl"]==-50
    assert s["trades"]==1
    assert s["loss_streak"]==1
    assert s["production"]=="BLOCKED"

def test_blocks_after_close(tmp_path):
    m=mgr(tmp_path)
    m.open_session()
    m.close_session()
    r=m.pre_trade_check(100)
    assert r["decision"]=="BLOCK_SESSION_CLOSED"

def test_blocks_daily_loss_limit(tmp_path):
    m=mgr(tmp_path)
    m.open_session()
    r=m.pre_trade_check(6000)
    assert r["decision"]=="BLOCK_DAILY_LOSS_LIMIT"

def test_ledger_written(tmp_path):
    m=mgr(tmp_path)
    m.open_session()
    assert Path(tmp_path/"ledger.jsonl").exists()
