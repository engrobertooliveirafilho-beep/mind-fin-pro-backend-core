from pathlib import Path
from mind_trader.app.security.institutional_live_lock import institutional_live_lock, assert_not_live_action

def test_blocks_live_trade():
    r=institutional_live_lock("LIVE_TRADE",{"symbol":"WIN"})
    assert r["blocked"] is True
    assert r["decision"]=="FORCE_BLOCK_LIVE_OR_PRODUCTION"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"

def test_blocks_broker_send_order():
    ok,reason=assert_not_live_action("BROKER_SEND_ORDER")
    assert ok is False
    assert reason=="FORCE_BLOCK_LIVE_OR_PRODUCTION"

def test_allows_research_action():
    ok,reason=assert_not_live_action("PAPER_RESEARCH")
    assert ok is True
    assert reason=="ALLOW_NON_LIVE_RESEARCH_ACTION"

def test_live_lock_report_written():
    institutional_live_lock("LIVE_TRADE")
    assert Path("mind_trader/reports/P8.92_institutional_live_lock.json").exists()
