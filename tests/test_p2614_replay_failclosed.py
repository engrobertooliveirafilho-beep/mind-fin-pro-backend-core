from datetime import datetime,timedelta
from app.runtime.p2614_real_fill_replay.execution import edge_signal,simulate_fill

def candles(n=25):
    t=datetime(2026,1,1)
    return [dict(time=t+timedelta(minutes=i),open=100.,close=100.1,high=100.2,low=99.9) for i in range(n)]
FT=dict(session="US_AFTERNOON",trend="TREND_UP",regime="LOW_VOL",wick_ratio=.5,body_ratio=.5,atr=1.,atr_med=1.)
BASE=dict(family="TREND",direction="BUY_PAPER",risk_model="ATR_STOP")

def test_valid_paper():
    assert edge_signal(BASE,FT)
    r=simulate_fill(BASE,candles(),{1:FT},1)
    assert r is not None and r["real_execution_allowed"] is False

def test_unknown_family_denied():
    assert edge_signal({**BASE,"family":"UNRECOGNIZED"},FT) is False

def test_unknown_direction_denied():
    assert edge_signal({**BASE,"direction":"BUY_REAL"},FT) is False
    assert simulate_fill({**BASE,"direction":"BUY_REAL"},candles(),{1:FT},1) is None

def test_missing_direction_denied():
    assert edge_signal({**BASE,"direction":None},FT) is False

def test_negative_cost_denied():
    assert simulate_fill(BASE,candles(),{1:FT},1,spread_r=-1) is None

def test_nan_cost_denied():
    assert simulate_fill(BASE,candles(),{1:FT},1,slippage_r=float("nan")) is None

def test_invalid_index_denied():
    assert simulate_fill(BASE,candles(),{1:FT},-1) is None

def test_invalid_features_denied():
    assert simulate_fill(BASE,candles(),None,1) is None
