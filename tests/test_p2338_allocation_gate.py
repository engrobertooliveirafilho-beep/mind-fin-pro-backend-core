import pytest
from app.runtime.p2338_allocation_gate import simulate_allocation

def ev():
    return ({"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","rankable_symbols":"0","total_trades":"1"},
            {"gate_decision":"NO_REBALANCE"},
            {"authority":"APPROVED_POLICY_ARTIFACT","min_closed_trades_per_symbol":30})
def test_current_sample_blocks_allocation():
    r=simulate_allocation(ranking=ev()[0],rebalance=ev()[1],policy=ev()[2],capital="10000")
    assert r["status"]=="BLOCKED_INSUFFICIENT_FORWARD_SAMPLE" and r["capital_allocated"]==0
def test_missing_policy_blocks_closed():
    x=ev();x=(x[0],x[1],{})
    assert simulate_allocation(ranking=x[0],rebalance=x[1],policy=x[2],capital="10000")["status"]=="BLOCKED_MISSING_APPROVED_SAMPLE_POLICY"
@pytest.mark.parametrize("capital",["0","-1","NaN","Infinity","bad"])
def test_invalid_capital(capital):
    x=ev()
    with pytest.raises(ValueError):simulate_allocation(ranking=x[0],rebalance=x[1],policy=x[2],capital=capital)
@pytest.mark.parametrize("key,value",[
 ("mode","LIVE"),("real_orders","ALLOWED"),("ftmo_real","ALLOWED"),
 ("rankable_symbols","1"),("total_trades","30")])
def test_inconsistent_or_unsafe_rank(key,value):
    x=ev();x[0][key]=value
    with pytest.raises(ValueError):simulate_allocation(ranking=x[0],rebalance=x[1],policy=x[2],capital="10000")
def test_wrong_rebalance_state_rejected():
    x=ev();x[1]["gate_decision"]="REBALANCE"
    with pytest.raises(ValueError):simulate_allocation(ranking=x[0],rebalance=x[1],policy=x[2],capital="10000")
