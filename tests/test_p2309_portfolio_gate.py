import pytest
from app.runtime.p2309_portfolio_gate import reconcile

def evidence():
    ger=[dict(symbol='GER40',timeframe='H1',exit_model='TIME_EXIT',source='P2299_APPROVED_EDGE',status='PAPER_WATCH_APPROVED') for _ in range(4)]
    non=[dict(symbol=s,timeframe='D1D1',family='EMA_CROSSEMA_CROSS',status='PAPER_WATCH_CANDIDATE_REQUIRES_BACKTEST') for s in ['EURUSD','GBPUSD','JP225']]
    for row in ger+non: row.update(mode='PAPER_ONLY',real_orders='FORBIDDEN',ftmo_real='FORBIDDEN',lot='0.01')
    return ger+non,dict(closed_trades='0',trades_consumed='0'),dict(portfolio_rows='7',unique_symbols='4')

def test_historical_is_not_certified():
    r=reconcile(*evidence());assert r['malformed_candidate_symbols']==['EURUSD','GBPUSD','JP225'];assert not r['promotion_allowed']
@pytest.mark.parametrize('key,bad',[('mode','LIVE'),('real_orders','ALLOWED'),('ftmo_real','ALLOWED'),('lot','1')])
def test_unsafe_row(key,bad):
    x=list(evidence());x[0][0][key]=bad
    with pytest.raises(ValueError):reconcile(*x)
@pytest.mark.parametrize('key,bad',[('closed_trades','1'),('trades_consumed','1')])
def test_unverified_performance(key,bad):
    x=list(evidence());x[1][key]=bad
    with pytest.raises(ValueError):reconcile(*x)
def test_candidate_promotion_blocked():
    x=list(evidence());x[0][4]['status']='PAPER_WATCH_APPROVED'
    with pytest.raises(ValueError):reconcile(*x)
def test_risk_count_mismatch():
    x=list(evidence());x[2]['unique_symbols']='10'
    with pytest.raises(ValueError):reconcile(*x)
