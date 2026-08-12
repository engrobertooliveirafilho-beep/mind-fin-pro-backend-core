from pathlib import Path
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
    g=ExecutionGateway(str(tmp_path/"exec.jsonl"),str(cfg),str(tmp_path/"session.json"),str(tmp_path/"day.jsonl"))
    return g

def test_gateway_blocks_paper_without_open_session(tmp_path):
    g=gateway(tmp_path)
    r=g.submit_order("PAPER",trade(),regime(),genome())
    assert r["decision"]=="BLOCKED_PAPER_SESSION"
    assert r["production"]=="BLOCKED"

def test_gateway_accepts_paper_with_open_session(tmp_path):
    g=gateway(tmp_path)
    g.paper.open_session()
    r=g.submit_order("PAPER",trade(),regime(),genome())
    assert r["decision"]=="ACCEPT_SIMULATED_ORDER"
    assert any(c["layer"]=="PAPER_SESSION" for c in r["checks"])

def test_gateway_blocks_paper_after_session_closed(tmp_path):
    g=gateway(tmp_path)
    g.paper.open_session()
    g.paper.close_session()
    r=g.submit_order("PAPER",trade(),regime(),genome())
    assert r["decision"]=="BLOCKED_PAPER_SESSION"
    assert r["session_check"]["decision"]=="BLOCK_SESSION_CLOSED"

def test_gateway_replay_does_not_require_paper_session(tmp_path):
    g=gateway(tmp_path)
    r=g.submit_order("REPLAY",trade(),regime(),genome())
    assert r["decision"]=="ACCEPT_SIMULATED_ORDER"

def test_gateway_paper_daily_loss_blocks(tmp_path):
    g=gateway(tmp_path)
    g.paper.open_session()
    t=trade(); t["risk_amount"]=6000
    r=g.submit_order("PAPER",t,regime(),genome())
    assert r["decision"]=="BLOCKED_PAPER_SESSION"
    assert r["session_check"]["decision"]=="BLOCK_DAILY_LOSS_LIMIT"
