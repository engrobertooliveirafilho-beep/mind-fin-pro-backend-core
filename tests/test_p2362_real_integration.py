import pytest
from app.runtime.p2362_full_signal_decision_pipeline import decide_signal
S=dict(symbol='EURUSD',side='BUY',strategy='SCALP',expected_payoff=3,base_lot=.01,entry=1.1,stop=1.09)
C=dict(swing_high=1.12,swing_low=1.09,atr=.01,adx=30,spread=1,timeframe='M1',breakout=True,atr_expansion=True,volume_impulse=True,m1_confirm=True,m5_confirm=True,h1_bias=True,spread_ok=True,last_loss=False,correlation_ok=True,governance_ok=True,current_drawdown=0,rebuild_after_profit=False,regime='TRENDING',structure='BREAKOUT')
def test_positive():
    r=decide_signal(S,C); assert r['final_decision']=='EMIT_TO_MT5_PAPER' and 0<r['paper_lot']<=.01
@pytest.mark.parametrize('key,value',[('governance_ok',False),('correlation_ok','True'),('spread',3),('last_loss',None),('last_loss',True),('adx',None),('structure','UNKNOWN'),('current_drawdown',11)])
def test_context_block(key,value):
    r=decide_signal(S,dict(C,**{key:value})); assert r['paper_lot']==0 and r['real_orders']=='FORBIDDEN'
@pytest.mark.parametrize('key,value',[('strategy',None),('strategy','NOT_TREND'),('expected_payoff',2),('side','UNKNOWN'),('base_lot',.02),('stop',1.2)])
def test_signal_block(key,value):
    r=decide_signal(dict(S,**{key:value}),C); assert r['paper_lot']==0 and r['real_orders']=='FORBIDDEN'
