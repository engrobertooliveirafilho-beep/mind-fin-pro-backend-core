import pytest
from app.runtime.p2311_p2314_filebridge_reconciliation import reconcile_filebridge

def evidence():
    signal="GER40,BUY,0.01,P2311_ACTIVE_TEST,2026-06-22T14:27:15"
    return [
        {"mode":"PAPER_ONLY","real_orders":"FORBIDDEN"},
        {"paper_forward":"REOPENED","p2310_blocker":"MT5_FILEBRIDGE_PENDING_CONSUMPTION"},
        {"write_status":"SKIPPED_PENDING_SIGNAL_EXISTS","previous_signal_exists":"True","previous_content":signal},
        {"consumption_status":"PENDING_AFTER_PARSE_OR_NOT_DELETED","signal_exists":"True",
         "signal_content":signal,"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN"},
    ]

def test_original_p2311_p2314_not_certified():
    result=reconcile_filebridge(*evidence())
    assert result["historical_resolved_claim_overridden"]
    assert result["stale_signal_present"] and not result["terminal_read_proven"]
    assert result["orders_authorized"]==0 and not result["e2e_certified"]

@pytest.mark.parametrize("index,key,bad",[
    (0,"mode","LIVE"),(0,"real_orders","ALLOWED"),
    (1,"paper_forward","CLOSED"),(1,"p2310_blocker","RESOLVED"),
    (2,"write_status","WRITTEN"),(2,"previous_signal_exists","False"),
    (2,"previous_content","GER40,SELL,0.01,P2311_ACTIVE_TEST,2026-06-22T14:27:15"),
    (3,"consumption_status","CONSUMED"),(3,"signal_exists","False"),
    (3,"mode","LIVE"),(3,"real_orders","ALLOWED"),(3,"ftmo_real","ALLOWED"),
])
def test_fail_closed(index,key,bad):
    x=evidence();x[index][key]=bad
    with pytest.raises(ValueError):reconcile_filebridge(*x)
