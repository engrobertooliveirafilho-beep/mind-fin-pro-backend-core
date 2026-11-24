import pytest
from app.runtime.p2366_institutional_targeting_engine import institutional_targets as target
@pytest.mark.parametrize('side,stop,level',[('BUY',1.12344,1.12349),('SELL',1.12346,1.12341)])
def test_precision(side,stop,level):
    r=target(dict(side=side,entry=1.12345,stop=stop,round_number=level))
    assert r['approved'] and r['target']==level and r['risk']>0
    assert r['rr']==pytest.approx(abs(level-1.12345)/abs(stop-1.12345))
    assert r['real_orders']=='FORBIDDEN'
@pytest.mark.parametrize('ctx',[dict(side='SELL',entry=1,stop=2,session_low=.1),dict(side='BUY',entry=1e308,stop=1,atr=1),dict(side='BUY',entry=1,stop=.9,atr=0),dict(side='BUY',entry=1,stop=.9,atr=float('nan'))])
def test_block(ctx):
    assert target(ctx)['approved'] is False
