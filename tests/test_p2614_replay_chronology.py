from datetime import datetime,timedelta
import pytest
from app.runtime.p2614_real_fill_replay import replay as mod
C=[dict(time=datetime(2026,1,1)+timedelta(minutes=i)) for i in range(90)]
E=[dict(edge_id="e1",family="TREND",direction="BUY_PAPER")]
def fill(e,c,f,i,*args):
    return dict(signal_i=i,entry_i=i+1,exit_i=i+4,r=1.0,real_execution_allowed=False)
def test_chronological_settlement(monkeypatch):
    monkeypatch.setattr(mod,"simulate_fill",fill)
    summary,curve,trades=mod.replay_portfolio("paper",E,C,{})
    assert summary["trades"]>0
    assert curve[0]["capital"]==100
    assert curve[3]["capital"]==100
    assert curve[4]["capital"]>100
    assert all(t["exit_i"]>t["entry_i"]>t["signal_i"] for t in trades)
def test_no_overlap(monkeypatch):
    monkeypatch.setattr(mod,"simulate_fill",fill)
    _,_,trades=mod.replay_portfolio("paper",E,C,{})
    assert all(b["signal_i"]>=a["exit_i"] for a,b in zip(trades,trades[1:]))
@pytest.mark.parametrize("kwargs",[{"risk_pct":-1},{"risk_pct":float("nan")},{"initial_capital":0},{"spread_r":-1},{"max_trades_per_day":0}])
def test_invalid_risk(kwargs):
    with pytest.raises(ValueError):mod.replay_portfolio("paper",E,C,{},**kwargs)
def test_duplicate_edges():
    with pytest.raises(ValueError):mod.replay_portfolio("paper",E*2,C,{})
def test_paper_only(monkeypatch):
    monkeypatch.setattr(mod,"simulate_fill",fill)
    s,_,trades=mod.replay_portfolio("paper",E,C,{})
    assert s["real_execution_allowed"] is False
    assert all(t["real_execution_allowed"] is False for t in trades)
