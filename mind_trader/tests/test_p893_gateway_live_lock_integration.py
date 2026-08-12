from mind_trader.app.execution.gateway import ExecutionGateway
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

def trade():
    return {"symbol":"WIN","strategy_id":"S1","entry":100,"stop":98,"target":104,"risk_amount":500,"open_risk":0,"daily_pnl":0,"total_pnl":0,"daily_trades":1,"loss_streak":0}

def regime():
    return {"regime":"TREND_UP","normalized_atr":0.005,"trade_allowed":True}

def genome():
    return {"genome_id":"g1","regime":"TREND_UP","edge_claim":"NONE"}

def gateway(tmp_path):
    cfg=tmp_path/"ftmo.json"
    save_default_ftmo_config(str(cfg))
    return ExecutionGateway(str(tmp_path/"ledger.jsonl"),str(cfg),str(tmp_path/"session.json"),str(tmp_path/"day.jsonl"))

def test_gateway_live_mode_hits_institutional_lock(tmp_path):
    g=gateway(tmp_path)
    r=g.submit_order("LIVE",trade(),regime(),genome())
    assert r["decision"]=="FORCE_BLOCK_LIVE_OR_PRODUCTION"
    assert r["live_lock"]["blocked"] is True
    assert r["production"]=="BLOCKED"

def test_gateway_broker_mode_hits_institutional_lock(tmp_path):
    g=gateway(tmp_path)
    r=g.submit_order("BROKER",trade(),regime(),genome())
    assert r["decision"]=="FORCE_BLOCK_LIVE_OR_PRODUCTION"
    assert r["live_lock"]["action"]=="BROKER_SEND_ORDER"
