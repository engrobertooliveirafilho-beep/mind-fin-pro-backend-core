import pytest
from app.runtime.p2303_mt5_consumption_audit import audit_consumption

def sample():
    return dict(mode="PAPER_ONLY",real_orders="FORBIDDEN",ftmo_real="FORBIDDEN",
      consumption_status="PENDING_MT5_CONSUMPTION",exists_now=True,
      selected_signal_id="P2302_5ed23464b49d",selected_symbol="GER40",
      selected_action="BUY",selected_lot="0.01",
      content_now="GER40,BUY,0.01,P2302_5ed23464b49d,2026-06-22T12:39:41")

def test_original_record_not_consumption():
    r=audit_consumption(sample(),[{"contains_signal_id":"False"}])
    assert r["logs_checked"]==1 and not r["terminal_read_proven"]
    assert r["orders_authorized"]==0 and not r["e2e_certified"]

@pytest.mark.parametrize("field,value",[
    ("mode","LIVE"),("real_orders","ALLOWED"),("ftmo_real","ALLOWED"),
    ("consumption_status","EXECUTED"),("exists_now",False),
    ("selected_signal_id","LIVE_123"),("content_now","GER40,SELL,0.01,FAKE")
])
def test_bad_evidence_rejected(field,value):
    x=sample()
    x[field]=value
    with pytest.raises(ValueError):audit_consumption(x,[])

def test_log_metadata_cannot_certify_fill():
    r=audit_consumption(sample(),[{"contains_signal_id":"True"}])
    assert r["matching_log_metadata"]==1
    assert not r["demo_fill_proven"] and not r["terminal_read_proven"]
