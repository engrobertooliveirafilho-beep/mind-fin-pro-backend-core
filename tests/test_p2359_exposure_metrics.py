import pytest
from app.runtime.p2359_real_correlation_exposure_engine import normalized_currency_exposure, correlation_precheck
@pytest.mark.parametrize('symbol,side,lot',[('XXX','BUY',.01),('EURUSD','HOLD',.01),('EURUSD','BUY',-1),('EURUSD','BUY',float('inf')),('EURUSD','BUY',True),('EURUSD','BUY',None)])
def test_invalid(symbol,side,lot):
    with pytest.raises(ValueError): normalized_currency_exposure(symbol,side,lot)
def test_limit():
    t=dict(symbol='EURUSD',side='BUY',lot=.01)
    assert correlation_precheck([t],t)['approved']
    assert not correlation_precheck([t,t],t)['approved']
