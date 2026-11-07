"""ET665.CG: malformed optional fields must fail closed before broker/validators."""
import json
from unittest.mock import Mock
import pytest
import mind_trader.app.execution.gateway as gateway_module
from mind_trader.app.execution.gateway import ExecutionGateway

BASE={"symbol":"EURUSD","strategy_id":"strategy_test","entry":1.1,"stop":1.0,"target":1.2,"risk_amount":1.0}
CASES=[
    ("stop","bad"),("stop",float("nan")),("stop",float("inf")),("stop",True),
    ("open_risk","bad"),("open_risk",-1),("open_risk",float("inf")),
    ("daily_pnl",None),("daily_pnl",float("nan")),
    ("total_pnl","bad"),("total_pnl",float("-inf")),
    ("daily_trades","2"),("daily_trades",-1),("daily_trades",True),
    ("loss_streak",1.5),("loss_streak",-1),
    ("session_allowed","false"),("news_blocked",1),
    ("side","HOLD"),("side",None),
]

@pytest.mark.parametrize("field,value",CASES)
@pytest.mark.parametrize("mode",["PAPER","REPLAY","MICRO_SIM"])
def test_optional_malformed_fields_block_before_any_broker_or_validation(tmp_path,monkeypatch,mode,field,value):
    broker=Mock(side_effect=AssertionError("broker must not run"))
    monkeypatch.setattr(gateway_module,"paper_route_order",broker)
    instance=ExecutionGateway.__new__(ExecutionGateway)
    instance.ledger_path=str(tmp_path/"ledger.jsonl")
    instance.paper=Mock()
    instance.risk=Mock()
    instance.ftmo=Mock()
    instance.adv=Mock()
    payload=dict(BASE)
    payload[field]=value
    result=instance.submit_order(mode,payload,{}, {})
    assert result["decision"]=="BLOCKED_INVALID_ORDER_FIELDS"
    assert result["production"]=="BLOCKED"
    broker.assert_not_called()
    instance.paper.assert_not_called()
    instance.risk.assert_not_called()
    instance.ftmo.assert_not_called()
    instance.adv.assert_not_called()
    records=[json.loads(line) for line in (tmp_path/"ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(records)==1
    assert records[0]["decision"]=="BLOCKED_INVALID_ORDER_FIELDS"
