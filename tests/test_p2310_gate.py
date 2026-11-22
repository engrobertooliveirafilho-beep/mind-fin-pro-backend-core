import pytest
from app.runtime.p2310_gate import reconcile_snapshot

def fixture():
    s={'real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN','mt5_consumption_status':'PENDING_MT5_CONSUMPTION'}
    c={'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN',
       'monte_carlo':'P2300_PASS_4_OF_4','spread_slippage_stress':'P2301_PASS_4_OF_4',
       'mt5_consumption':'PENDING_MT5_CONSUMPTION',
       'paper_watch_portfolio':'7 rows / 4 symbols / PASS_MINIMUM_SYMBOL_DIVERSIFICATION'}
    b={'MT5_FILEBRIDGE_PENDING_CONSUMPTION':'OPEN'}
    return s,c,b

def test_original_claims_not_certified():
    result=reconcile_snapshot(*fixture())
    assert not result['e2e_certified'] and not result['stress_certified']
    assert result['orders_authorized']==0

@pytest.mark.parametrize('index,key,bad',[
    (0,'real_orders','ALLOWED'),(0,'ftmo_real','ALLOWED'),
    (0,'mt5_consumption_status','FILLED'),(1,'mode','LIVE'),
    (1,'real_orders','ALLOWED'),(1,'monte_carlo','CERTIFIED'),
    (1,'spread_slippage_stress','CERTIFIED'),(1,'mt5_consumption','CONSUMED'),
    (1,'paper_watch_portfolio','CERTIFIED'),(2,'MT5_FILEBRIDGE_PENDING_CONSUMPTION','CLOSED')])
def test_adversarial(index,key,bad):
    x=list(fixture());x[index][key]=bad
    with pytest.raises(ValueError):reconcile_snapshot(*x)
