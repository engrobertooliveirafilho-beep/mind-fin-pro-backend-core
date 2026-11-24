import pytest
from app.runtime.p2361_dynamic_position_sizing_engine import dynamic_paper_lot
BASE=dict(base_lot=.01,institutional_score=95,expected_payoff=3,current_drawdown=2,correlation_ok=True,last_trade_loss=False,rebuild_after_profit=False)
@pytest.mark.parametrize("key,value",[("correlation_ok","false"),("current_drawdown",-1),("base_lot",.02),("institutional_score",101),("expected_payoff",float("inf")),("last_trade_loss",1)])
def test_invalid(key,value):
    assert dynamic_paper_lot(BASE|{key:value})["recommended_paper_lot"]==0
def test_cap():
    assert dynamic_paper_lot(BASE)["recommended_paper_lot"]==.01
def test_loss():
    assert dynamic_paper_lot(BASE|{"last_trade_loss":True})["recommended_paper_lot"]==.005
def test_missing():
    assert dynamic_paper_lot({})["recommended_paper_lot"]==0
