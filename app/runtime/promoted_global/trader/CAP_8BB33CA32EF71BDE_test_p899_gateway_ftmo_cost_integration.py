from pathlib import Path
from mind_trader.app.execution.gateway import ExecutionGateway
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config, default_ftmo_config
import json

def trade():
    return {"symbol":"WIN","side":"BUY","strategy_id":"S1","entry":100,"stop":98,"target":104,"risk_amount":500,"open_risk":0,"daily_pnl":0,"total_pnl":0,"daily_trades":1,"loss_streak":0}

def regime():
    return {"regime":"TREND_UP","normalized_atr":0.005,"trade_allowed":True}

def genome():
    return {"genome_id":"g1","regime":"TREND_UP","edge_claim":"NONE"}

def test_gateway_paper_broker_uses_ftmo_cost_config(tmp_path):
    cfg=default_ftmo_config()
    cfg["spread"]=0.2
    cfg["slippage"]=0.1
    cfg["commission"]=1
    cfgp=tmp_path/"ftmo.json"
    cfgp.write_text(json.dumps(cfg),encoding="utf-8")

    g=ExecutionGateway(
        str(tmp_path/"exec.jsonl"),
        str(cfgp),
        str(tmp_path/"session.json"),
        str(tmp_path/"day.jsonl"),
        str(tmp_path/"paper_broker.jsonl")
    )
    g.paper.open_session()

    r=g.submit_order("PAPER",trade(),regime(),genome())

    assert r["decision"]=="ACCEPT_SIMULATED_ORDER"
    assert r["paper_broker"]["decision"]=="PAPER_ORDER_ACCEPTED"
    assert r["paper_broker"]["cost_source"]["decision"]=="FTMO_COST_CONFIG_OK"
    assert round(r["paper_broker"]["fill"]["fill_price"],10)==100.2
    assert r["real_broker_routing"]=="DISABLED"
    assert r["production"]=="BLOCKED"
