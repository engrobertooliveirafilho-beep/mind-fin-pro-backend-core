import pytest
from app.runtime.p2356_context_regime_edge_engine import score_context_edge
BASE=dict(trades=30,win_rate=60,payoff=3,profit_factor=1.5,expectancy=.2,max_drawdown=10)
@pytest.mark.parametrize('key,value',[('trades',True),('trades',30.5),('win_rate',101),('win_rate',-1),('payoff',float('inf')),('profit_factor',-1),('expectancy',float('nan')),('max_drawdown',-1),('max_drawdown',101),('payoff','3'),('payoff',10**400)])
def test_invalid(key,value):
    r=score_context_edge(dict(BASE,**{key:value}));assert r['passed'] is False and r['reason']=='INVALID_METRICS'
@pytest.mark.parametrize('key',list(BASE))
def test_missing(key):
    d=BASE.copy();del d[key];assert score_context_edge(d)['passed'] is False
def test_valid():
    assert score_context_edge(BASE)['passed'] is True
