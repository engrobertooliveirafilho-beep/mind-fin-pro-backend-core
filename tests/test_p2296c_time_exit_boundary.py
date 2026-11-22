"""Regression of original P2296C TIME_EXIT boundary (not a synthetic performance claim)."""
from app.runtime.p2296c_real_exit_engine import simulate

def test_time_exit_exact_eighth_candle():
    rows=[]
    for i in range(35):
        row={"time":str(i),"open":100.0,"high":101.0,"low":99.0,
             "close":100.0,"atr_14":1.0,"body_pct":0.1,
             "session":"LONDON","volatility_state":"HIGH",
             "spread_state":"NORMAL","trend_21_55":"UP"}
        rows.append(row)
    rows[20]["open"]=100.0
    rows[20]["close"]=99.5
    rows[20]["body_pct"]=0.8
    rows[28]["close"]=102.0
    trades=simulate(rows,"TIME_EXIT")
    assert len(trades)==1
    assert trades[0]["exit_time"]=="28"
    assert trades[0]["exit_reason"]=="TIME_EXIT"
    assert trades[0]["pnl"]==2.0
