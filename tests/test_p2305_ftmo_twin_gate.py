import pytest
from app.runtime.p2305_ftmo_twin_gate import reconcile_twin

def fixture():
    s={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
       "ftmo_twin_status":"FTMO_TWIN_PASS","trades_consumed":"0","trades_day":"1",
       "daily_loss_pct":"0","total_loss_pct":"0"}
    state={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
           "status":"FTMO_TWIN_PASS","trades_consumed":"0","trades_day":"1"}
    rules={"daily_loss_limit_pct":"1.0","total_loss_limit_pct":"5.0",
           "max_trades_day":"6","max_trades_edge_day":"2","max_exposure_lots":"0.01",
           "default_lot":"0.01","risk_block_only":"TRUE",
           "real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN"}
    return s,state,rules

def test_original_ftmo_twin_not_certified():
    r=reconcile_twin(*fixture())
    assert r["historical_twin_pass"] and not r["ftmo_challenge_certified"]
    assert not r["performance_certified"] and not r["e2e_certified"]

@pytest.mark.parametrize("which,key,bad",[
    (0,"mode","LIVE"),(1,"real_orders","ALLOWED"),(2,"ftmo_real","ALLOWED"),
    (2,"risk_block_only","FALSE"),(2,"max_exposure_lots","1"),
    (0,"trades_consumed","1"),(1,"trades_day","2"),
    (0,"daily_loss_pct","2"),(0,"total_loss_pct","6"),
    (0,"daily_loss_pct","NaN"),(2,"max_trades_day","inf"),
])
def test_fail_closed(which,key,bad):
    x=list(fixture())
    x[which][key]=bad
    with pytest.raises(ValueError):reconcile_twin(*x)
