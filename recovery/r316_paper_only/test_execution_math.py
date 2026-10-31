import pytest
from execution_math import resolve_exit, execution_price, trade_r

def test_buy_both_stop_first():
    assert resolve_exit('BUY',111,94,95,110)==('stop',95)
def test_sell_both_stop_first():
    assert resolve_exit('SELL',106,89,105,90)==('stop',105)
def test_target_only():
    assert resolve_exit('BUY',111,99,95,110)==('target',110)
    assert resolve_exit('SELL',101,89,105,90)==('target',90)
def test_buy_costs_are_adverse():
    assert trade_r('BUY',100,95,110,10) < trade_r('BUY',100,95,110,0)
    assert trade_r('BUY',100,95,95,10) < -1
def test_sell_costs_are_adverse():
    assert trade_r('SELL',100,105,90,10) < trade_r('SELL',100,105,90,0)
    assert trade_r('SELL',100,105,105,10) < -1
def test_cost_zero_symmetry():
    assert trade_r('BUY',100,95,110)==pytest.approx(2)
    assert trade_r('SELL',100,105,90)==pytest.approx(2)
def test_invalid_prices_fail_closed():
    with pytest.raises(ValueError): resolve_exit('BUY',90,110,95,110)
    with pytest.raises(ValueError): trade_r('SELL',100,95,90)
    with pytest.raises(ValueError): execution_price(100,'BUY',-1)
def test_no_hit():
    assert resolve_exit('BUY',101,99,95,110)==(None,None)
