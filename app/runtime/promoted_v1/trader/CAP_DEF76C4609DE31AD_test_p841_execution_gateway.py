from pathlib import Path
from mind_trader.app.execution.gateway import ExecutionGateway, broker_contracts
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
    g=ExecutionGateway(str(tmp_path/"ledger.jsonl"),str(cfg),str(tmp_path/"session.json"),str(tmp_path/"day.jsonl"))
    g.paper.open_session()
    return g

def test_blocks_live_execution(tmp_path):
    g=gateway(tmp_path)
    r=g.submit_order("LIVE",trade(),regime(),genome())
    assert r["decision"]=="FORCE_BLOCK_LIVE_OR_PRODUCTION"
    assert r["production"]=="BLOCKED"

def test_accepts_simulated_order_when_all_checks_pass(tmp_path):
    g=gateway(tmp_path)
    r=g.submit_order("PAPER",trade(),regime(),genome())
    assert r["decision"]=="ACCEPT_SIMULATED_ORDER"
    assert r["real_broker_routing"]=="DISABLED"

def test_rejects_no_stop(tmp_path):
    t=trade(); t["stop"]=None
    g=gateway(tmp_path)
    r=g.submit_order("PAPER",t,regime(),genome())
    assert r["decision"]=="REJECT_ORDER"

def test_rejects_undefined_regime(tmp_path):
    rg={"regime":"UNDEFINED","trade_allowed":False}
    g=gateway(tmp_path)
    r=g.submit_order("PAPER",trade(),rg,genome())
    assert r["decision"]=="REJECT_ORDER"

def test_broker_contracts_disabled_for_real_execution():
    c=broker_contracts()
    assert c["production"]=="BLOCKED"
    assert c["MT5"]["status"]=="CONTRACT_PLACEHOLDER_DISABLED_FOR_REAL_EXECUTION"

def test_execution_ledger_written(tmp_path):
    p=tmp_path/"ledger.jsonl"
    cfg=tmp_path/"ftmo.json"
    save_default_ftmo_config(str(cfg))
    g=ExecutionGateway(str(p),str(cfg),str(tmp_path/"session.json"),str(tmp_path/"day.jsonl"))
    g.paper.open_session()
    g.submit_order("PAPER",trade(),regime(),genome())
    assert p.exists()

