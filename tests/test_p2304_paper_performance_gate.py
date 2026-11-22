import pytest
from app.runtime.p2304_paper_performance_gate import audit_paper_performance

def sample():
    summary={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","trades_sent":"1","trades_consumed":"0","open_or_pending":"1"}
    ledger=[{"signal_id":"P2302_5ed23464b49d","mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","trade_status":"NOT_CONSUMED_YET","consumption_status":"PENDING_MT5_CONSUMPTION","pnl":"0","pnl_pct":"0"}]
    risk=[{"metric":"trades_consumed","value":"0"},{"metric":"real_orders","value":"FORBIDDEN"},{"metric":"ftmo_real","value":"FORBIDDEN"}]
    return summary,ledger,risk

def test_historical_not_certified():
    r=audit_paper_performance(*sample())
    assert r["signals_sent"]==1 and r["signals_consumed_reported"]==0
    assert r["closed_trades_reported"]==0
    assert not r["ftmo_compliance_certified"] and not r["performance_certified"]

@pytest.mark.parametrize("field,bad",[("mode","LIVE"),("real_orders","ALLOWED"),("ftmo_real","ALLOWED"),("trades_consumed","1"),("open_or_pending","0")])
def test_summary_fail_closed(field,bad):
    s,l,r=sample()
    s[field]=bad
    with pytest.raises(ValueError):audit_paper_performance(s,l,r)

@pytest.mark.parametrize("field,bad",[("trade_status","CLOSED"),("pnl","100"),("consumption_status","FILLED"),("real_orders","ALLOWED")])
def test_ledger_fail_closed(field,bad):
    s,l,r=sample()
    l[0][field]=bad
    with pytest.raises(ValueError):audit_paper_performance(s,l,r)

def test_risk_ledger_mismatch():
    s,l,r=sample()
    r[0]["value"]="1"
    with pytest.raises(ValueError):audit_paper_performance(s,l,r)
