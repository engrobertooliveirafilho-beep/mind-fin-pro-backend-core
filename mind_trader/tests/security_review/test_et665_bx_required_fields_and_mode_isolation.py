"""ET665.BX: fail-closed field validation and replay/micro-sim broker isolation."""
import json
from types import SimpleNamespace
import pytest
import mind_trader.app.execution.gateway as gateway_module
from mind_trader.app.execution.gateway import ExecutionGateway

BASE={"symbol":"EURUSD","strategy_id":"strategy_test","entry":1.1,"target":1.2,"risk_amount":1.0}

@pytest.mark.parametrize("mutation,decision", [
    ({"symbol":None},"BLOCKED_INVALID_ORDER_FIELDS"),
    ({"strategy_id":""},"BLOCKED_INVALID_ORDER_FIELDS"),
    ({"entry":None},"BLOCKED_INVALID_ORDER_FIELDS"),
    ({"entry":float("nan")},"BLOCKED_INVALID_ORDER_FIELDS"),
    ({"target":float("inf")},"BLOCKED_INVALID_ORDER_FIELDS"),
    ({"risk_amount":0},"BLOCKED_INVALID_ORDER_FIELDS"),
    ({"risk_amount":True},"BLOCKED_INVALID_ORDER_FIELDS"),
    ({"symbol":"__REMOVE__"},"BLOCKED_MISSING_ORDER_FIELDS"),
    ({"target":"__REMOVE__"},"BLOCKED_MISSING_ORDER_FIELDS"),
])
def test_required_fields_fail_closed_without_broker(tmp_path,monkeypatch,mutation,decision):
    def forbidden(*args,**kwargs):
        raise AssertionError("broker route invoked")
    monkeypatch.setattr(gateway_module,"paper_route_order",forbidden)
    instance=ExecutionGateway.__new__(ExecutionGateway)
    instance.ledger_path=str(tmp_path/"ledger.jsonl")
    payload=dict(BASE)
    for key,value in mutation.items():
        if value=="__REMOVE__":
            payload.pop(key)
        else:
            payload[key]=value
    result=instance.submit_order("PAPER",payload,{}, {})
    assert result["decision"]==decision
    assert result["production"]=="BLOCKED"
    records=[json.loads(x) for x in (tmp_path/"ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(records)==1 and records[0]["decision"]==decision

@pytest.mark.parametrize("mode",["REPLAY","MICRO_SIM"])
def test_nonpaper_modes_never_route_broker_even_when_checks_pass(tmp_path,monkeypatch,mode):
    def forbidden(*args,**kwargs):
        raise AssertionError("broker route invoked")
    monkeypatch.setattr(gateway_module,"paper_route_order",forbidden)
    monkeypatch.setattr(gateway_module,"TradeIntent",lambda **kwargs: SimpleNamespace(**kwargs))
    monkeypatch.setattr(gateway_module,"audit_rule_application",lambda *args:{"decision":"ALLOW_FTMO_SIMULATION"})
    monkeypatch.setattr(gateway_module,"require_defined_regime",lambda *args:(True,"OK"))
    instance=ExecutionGateway.__new__(ExecutionGateway)
    instance.ledger_path=str(tmp_path/"ledger.jsonl")
    instance.paper_broker_ledger_path=str(tmp_path/"broker.jsonl")
    instance.ftmo_config_valid={"valid":True,"hash":"test"}
    instance.ftmo_ruleset={"version":"test"}
    instance.ftmo=SimpleNamespace(validate=lambda *args:(True,"OK"))
    instance.risk=SimpleNamespace(validate=lambda *args:(True,"OK"))
    instance.adv=SimpleNamespace(review_trade=lambda *args:{"adversarial_passed":True,"decision":"OK"})
    instance.paper=SimpleNamespace(pre_trade_check=lambda *args:{"allowed":True,"decision":"OK"})
    result=instance.submit_order(mode,dict(BASE),{"regime":"TREND"},{"genome_id":"test"})
    assert result["decision"]=="ACCEPT_SIMULATED_ORDER"
    assert result["production"]=="BLOCKED"
    assert result["real_broker_routing"]=="DISABLED"
    assert result["paper_broker"] is None
    assert not (tmp_path/"broker.jsonl").exists()
