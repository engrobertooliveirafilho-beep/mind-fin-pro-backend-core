from pathlib import Path
import json
from mind_trader.app.execution.gateway import ExecutionGateway
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

def trade():
    return {"symbol":"WIN","side":"BUY","strategy_id":"S1","entry":100,"stop":98,"target":104,"risk_amount":500,"open_risk":0,"daily_pnl":0,"total_pnl":0,"daily_trades":1,"loss_streak":0}

def regime():
    return {"regime":"TREND_UP","normalized_atr":0.005,"trade_allowed":True}

def genome():
    return {"genome_id":"g1","regime":"TREND_UP","edge_claim":"NONE"}

def gateway(tmp_path):
    cfg=tmp_path/"ftmo.json"
    save_default_ftmo_config(str(cfg))
    config=json.loads(cfg.read_text(encoding="utf-8"))
    config.update(spread=0.2, slippage=0.1, commission=1.0)
    cfg.write_text(json.dumps(config),encoding="utf-8")
    g=ExecutionGateway(str(tmp_path/"exec.jsonl"),str(cfg),str(tmp_path/"session.json"),str(tmp_path/"day.jsonl"),str(tmp_path/"paper_broker.jsonl"))
    g.paper.open_session()
    return g

def test_gateway_routes_accepted_paper_order_to_paper_broker(tmp_path):
    g=gateway(tmp_path)
    r=g.submit_order("PAPER",trade(),regime(),genome())
    assert r["decision"]=="ACCEPT_SIMULATED_ORDER"
    assert r["paper_broker"]["decision"]=="PAPER_ORDER_ACCEPTED"
    assert Path(tmp_path/"paper_broker.jsonl").exists()
    assert r["real_broker_routing"]=="DISABLED"

def test_gateway_rejected_order_does_not_route_to_paper_broker(tmp_path):
    g=gateway(tmp_path)
    t=trade(); t["stop"]=None
    r=g.submit_order("PAPER",t,regime(),genome())
    assert r["decision"]=="REJECT_ORDER"
    assert r["paper_broker"] is None

def test_gateway_live_still_force_block(tmp_path):
    g=gateway(tmp_path)
    r=g.submit_order("LIVE",trade(),regime(),genome())
    assert r["decision"]=="FORCE_BLOCK_LIVE_OR_PRODUCTION"


def test_gateway_propagates_real_broker_cost_rejection(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    g = gateway(tmp_path)
    cfg = tmp_path / "ftmo.json"
    config = json.loads(cfg.read_text(encoding="utf-8"))
    config.update(spread=0, slippage=0, commission=0)
    cfg.write_text(json.dumps(config), encoding="utf-8")
    result = g.submit_order("PAPER", trade(), regime(), genome())
    assert result["decision"] == "REJECT_ORDER"
    assert result["order_status"] == "SIMULATED_REJECTED"
    assert result["paper_broker"]["decision"] == "PAPER_ORDER_REJECTED_INVALID_COST_CONFIG"
    assert result["real_broker_routing"] == "DISABLED"
    broker = json.loads((tmp_path / "paper_broker.jsonl").read_text().splitlines()[-1])
    execution = json.loads((tmp_path / "exec.jsonl").read_text().splitlines()[-1])
    assert execution["paper_broker"]["paper_order_id"] == broker["paper_order_id"]
    assert execution["decision"] == "REJECT_ORDER"

def test_gateway_rejects_missing_broker_response(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    g = gateway(tmp_path)
    monkeypatch.setattr("mind_trader.app.execution.gateway.paper_route_order", lambda *args, **kwargs: None)
    result = g.submit_order("PAPER", trade(), regime(), genome())
    assert result["decision"] == "REJECT_ORDER"
    assert result["order_status"] == "SIMULATED_REJECTED"
    assert any(c["layer"] == "PAPER_BROKER" and not c["ok"] for c in result["checks"])
