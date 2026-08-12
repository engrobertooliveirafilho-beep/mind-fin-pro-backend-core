import json
from mind_trader.app.execution.gateway import ExecutionGateway
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config, default_ftmo_config

def trade():
    return {"symbol":"WIN","strategy_id":"S1","entry":100,"stop":98,"target":104,"risk_amount":500,"open_risk":0,"daily_pnl":0,"total_pnl":0,"daily_trades":1,"loss_streak":0}

def regime():
    return {"regime":"TREND_UP","normalized_atr":0.005,"trade_allowed":True}

def genome():
    return {"genome_id":"g1","regime":"TREND_UP","edge_claim":"NONE"}

def test_gateway_blocks_missing_ftmo_config(tmp_path):
    g=ExecutionGateway(str(tmp_path/"ledger.jsonl"),str(tmp_path/"missing.json"),str(tmp_path/"session.json"),str(tmp_path/"day.jsonl"))
    r=g.submit_order("PAPER",trade(),regime(),genome())
    assert r["decision"]=="BLOCKED_INVALID_FTMO_CONFIG"
    assert r["production"]=="BLOCKED"

def test_gateway_uses_versioned_ftmo_config(tmp_path):
    cfg=tmp_path/"ftmo.json"; save_default_ftmo_config(str(cfg))
    g=ExecutionGateway(str(tmp_path/"ledger.jsonl"),str(cfg),str(tmp_path/"session.json"),str(tmp_path/"day.jsonl"))
    g.paper.open_session()
    r=g.submit_order("PAPER",trade(),regime(),genome())
    assert r["decision"]=="ACCEPT_SIMULATED_ORDER"
    assert r["ftmo_config_version"]=="P8.46_FTMO_RULESET_V1"
    assert len(r["ftmo_config_hash"])==64

def test_gateway_blocks_symbol_not_allowed_by_config(tmp_path):
    cfg=default_ftmo_config()
    cfg["allowed_symbols"]=["EURUSD"]
    p=tmp_path/"ftmo.json"
    p.write_text(json.dumps(cfg),encoding="utf-8")
    g=ExecutionGateway(str(tmp_path/"ledger.jsonl"),str(p),str(tmp_path/"session.json"),str(tmp_path/"day.jsonl"))
    g.paper.open_session()
    r=g.submit_order("PAPER",trade(),regime(),genome())
    assert r["decision"]=="REJECT_ORDER"
    assert r["production"]=="BLOCKED"
