import pytest
from app.runtime.p2343_post_loss_governance_gate import post_loss_gate

KEYS = ('m1','m5','m15','h1','trend_filter','volatility_filter','session_filter','support_resistance_filter')

@pytest.mark.parametrize('key', KEYS)
def test_missing_check_blocks(key):
    ctx = dict.fromkeys(KEYS, True)
    del ctx[key]
    assert post_loss_gate('EURUSD','BUY',True,ctx)['status'] == 'BLOCKED'

@pytest.mark.parametrize('value', [None, 0, '', 'False', 1])
def test_invalid_loss_state(value):
    assert post_loss_gate('EURUSD','BUY',value)['status'] == 'BLOCKED'

def test_approval():
    assert post_loss_gate('EURUSD','BUY',True,dict.fromkeys(KEYS,True))['status'] == 'APPROVED'
    assert post_loss_gate('EURUSD','SELL',False)['status'] == 'APPROVED'

def test_non_boolean_check():
    ctx = dict.fromkeys(KEYS,True)
    ctx['m1'] = 100
    assert post_loss_gate('EURUSD','BUY',True,ctx)['status'] == 'BLOCKED'

def test_invalid_identity():
    assert post_loss_gate('','BUY',False)['status'] == 'BLOCKED'
    assert post_loss_gate('EURUSD','UNKNOWN',False)['status'] == 'BLOCKED'
