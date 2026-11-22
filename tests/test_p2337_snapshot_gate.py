import pytest
from app.runtime.p2337_snapshot_gate import certify_snapshot

def evidence():
    c={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","capture_status":"CERTIFIED","deduplication":"APPLIED","captured_results":"1","unique_symbols":"1"}
    r={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","status":"CERTIFIED_PROVISIONAL_RANKING_SAMPLE_LIMITED","total_trades":"1","rankable_symbols":"0"}
    b={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","status":"CERTIFIED_GATE_BLOCKED_BY_SAMPLE_SIZE","gate_decision":"NO_REBALANCE","symbols_evaluated":"1"}
    return c,r,b

def test_snapshot_records_blocked_state():
    x=certify_snapshot(*evidence())
    assert x["status"]=="SNAPSHOT_CERTIFIED_BLOCKED_BY_SAMPLE_SIZE"
    assert not x["capital_allocation_allowed"] and not x["e2e_certified"]

@pytest.mark.parametrize("index,key,bad",[
 (0,"capture_status","PENDING"),(0,"deduplication","NOT_APPLIED"),
 (1,"rankable_symbols","1"),(1,"total_trades","10"),
 (2,"gate_decision","REBALANCE"),(2,"status","CERTIFIED_REBALANCE"),
 (0,"real_orders","ALLOWED"),(1,"ftmo_real","ALLOWED"),
])
def test_inconsistent_or_unsafe_evidence_rejected(index,key,bad):
    x=list(evidence());x[index][key]=bad
    with pytest.raises(ValueError):certify_snapshot(*x)
