from paper_risk_gate import authorize_paper_order

ORDER = {'mode':'PAPER','symbol':'EURUSD','risk_amount':'50'}
STATE = {'mode':'PAPER','authority_verified':True,'risk_guard_wired':True,'kill_switch':False,'force_no_trade':False,'initial_balance':'10000','equity':'10000','day_start_equity':'10000','open_positions':0,'correlated_positions':0}

def decision(order=None,state=None):
    return authorize_paper_order(ORDER if order is None else order, STATE if state is None else state)

def test_paper_only_approval_never_authorizes_real_orders():
    result=decision(); assert result['approved'] is True and result['real_orders_authorized'] is False

def test_live_mode_denied():
    assert decision({**ORDER,'mode':'LIVE'})['approved'] is False

def test_missing_authority_denied():
    assert decision(state={**STATE,'authority_verified':False})['approved'] is False

def test_unwired_guard_denied():
    assert decision(state={**STATE,'risk_guard_wired':False})['approved'] is False

def test_kill_switch_denied():
    assert decision(state={**STATE,'kill_switch':True})['approved'] is False

def test_force_no_trade_denied():
    assert decision(state={**STATE,'force_no_trade':True})['approved'] is False

def test_daily_loss_denied():
    assert decision(state={**STATE,'equity':'9610'})['approved'] is False

def test_total_loss_denied():
    assert decision(state={**STATE,'equity':'9200','day_start_equity':'9200'})['approved'] is False

def test_per_trade_risk_denied():
    assert decision({**ORDER,'risk_amount':'76'})['approved'] is False

def test_position_limit_denied():
    assert decision(state={**STATE,'open_positions':3})['approved'] is False

def test_correlated_limit_denied():
    assert decision(state={**STATE,'correlated_positions':2})['approved'] is False

def test_nan_denied():
    assert decision({**ORDER,'risk_amount':'NaN'})['approved'] is False

def test_negative_risk_denied():
    assert decision({**ORDER,'risk_amount':'-5'})['approved'] is False

def test_missing_state_denied():
    assert decision(state={})['approved'] is False
