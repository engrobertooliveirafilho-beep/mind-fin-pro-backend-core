import pytest
from app.runtime.p2302_forward_audit import audit_paper_forward

def fixture():
    state={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","max_signal_candle":1}
    rows=[dict(signal_id=f"P2302_{i}",symbol="GER40",timeframe="H1",lot="0.01",
               mode="PAPER_ONLY",real_orders="FORBIDDEN",ftmo_real="FORBIDDEN",
               status="PAPER_SIGNAL_GENERATED",candle_key="20260622_11_H1",
               action="BUY" if i<2 else "SELL") for i in range(4)]
    return rows,state

def test_original_drive_forward_invalid():
    rows,state=fixture()
    r=audit_paper_forward(rows,state)
    assert r["historical_signals"]==4 and r["duplicate_candle_signals"]==3
    assert r["conflicting_candles"]==1 and r["orders_authorized"]==0
    assert not r["mt5_consumption_certified"] and not r["e2e_certified"]

def test_single_paper_observation_not_e2e():
    rows,state=fixture()
    r=audit_paper_forward(rows[:1],state)
    assert r["status"]=="PAPER_OBSERVATION_ONLY" and not r["e2e_certified"]

@pytest.mark.parametrize("key,bad",[("mode","LIVE"),("real_orders","ALLOWED"),("ftmo_real","ALLOWED"),("max_signal_candle",4)])
def test_state_fail_closed(key,bad):
    rows,state=fixture()
    state[key]=bad
    with pytest.raises(ValueError):audit_paper_forward(rows,state)

@pytest.mark.parametrize("key,bad",[("symbol","EURUSD"),("lot","1.00"),("real_orders","ALLOWED"),("action","HOLD")])
def test_signal_fail_closed(key,bad):
    rows,state=fixture()
    rows[0][key]=bad
    with pytest.raises(ValueError):audit_paper_forward(rows,state)

def test_duplicate_signal_id_rejected():
    rows,state=fixture()
    rows[1]["signal_id"]=rows[0]["signal_id"]
    with pytest.raises(ValueError):audit_paper_forward(rows,state)
