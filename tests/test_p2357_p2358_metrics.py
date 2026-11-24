import pytest
from app.runtime.p2357_context_edge_walk_forward_validator import validate_walk_forward
from app.runtime.p2358_anti_overfit_context_edge_validator import anti_overfit_validate

WF=dict(train_profit_factor=2,test_profit_factor=1.8,train_payoff=3,test_payoff=3,test_max_drawdown=5,test_trades=40)
AO=dict(symbols_tested=3,years_tested=3,regimes_tested=3,out_of_sample_profit_factor=2,out_of_sample_payoff=3,out_of_sample_expectancy=1,max_drawdown=5,parameter_sensitivity=20)
@pytest.mark.parametrize('key,value',[('train_profit_factor',0),('test_profit_factor',float('inf')),('test_max_drawdown',-1),('test_trades',30.5),('train_payoff',float('nan'))])
def test_wf_invalid(key,value):
    assert validate_walk_forward([WF|{key:value}])['passed']==0
@pytest.mark.parametrize('key,value',[('symbols_tested',True),('out_of_sample_profit_factor',float('inf')),('max_drawdown',-1),('parameter_sensitivity',-1),('out_of_sample_expectancy',float('nan'))])
def test_ao_invalid(key,value):
    assert not anti_overfit_validate(AO|{key:value})['anti_overfit_passed']
def test_valid():
    assert validate_walk_forward([WF])['passed']==1
    assert anti_overfit_validate(AO)['anti_overfit_passed']
