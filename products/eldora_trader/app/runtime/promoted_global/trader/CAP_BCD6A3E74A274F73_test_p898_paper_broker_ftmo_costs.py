import json
from mind_trader.app.execution.paper_broker_adapter import paper_route_order, costs_from_ftmo_config
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

def order():
    return {"symbol":"WIN","side":"BUY","entry":100,"stop":98,"target":104,"risk_amount":500,"strategy_id":"S1"}

def test_costs_from_ftmo_config(tmp_path):
    cfg=default_ftmo_config()
    cfg["spread"]=0.2
    cfg["slippage"]=0.1
    cfg["commission"]=1
    p=tmp_path/"ftmo.json"
    p.write_text(json.dumps(cfg),encoding="utf-8")
    r=costs_from_ftmo_config(str(p))
    assert r["valid"] is True
    assert r["spread"]==0.2
    assert r["commission"]==1

def test_paper_route_uses_ftmo_costs(tmp_path):
    cfg=default_ftmo_config()
    cfg["spread"]=0.2
    cfg["slippage"]=0.1
    cfg["commission"]=1
    p=tmp_path/"ftmo.json"
    p.write_text(json.dumps(cfg),encoding="utf-8")
    r=paper_route_order(order(),ledger_path=str(tmp_path/"ledger.jsonl"),ftmo_config_path=str(p))
    assert r["decision"]=="PAPER_ORDER_ACCEPTED"
    assert round(r["fill"]["fill_price"],10)==100.2
    assert r["cost_source"]["decision"]=="FTMO_COST_CONFIG_OK"

def test_paper_route_blocks_invalid_cost_config(tmp_path):
    r=paper_route_order(order(),ledger_path=str(tmp_path/"ledger.jsonl"),ftmo_config_path=str(tmp_path/"missing.json"))
    assert r["decision"]=="PAPER_ORDER_REJECTED_INVALID_COST_CONFIG"
    assert r["production"]=="BLOCKED"
