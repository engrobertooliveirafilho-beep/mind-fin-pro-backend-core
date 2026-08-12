import json, uuid
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.execution.safe_broker_adapter import validate_order_payload
from mind_trader.app.execution.paper_fill_model import simulate_fill
from mind_trader.app.risk.ftmo_ruleset import load_ftmo_config

def write_paper_broker_ledger(event,path="mind_trader/logs/P8.95_PAPER_BROKER_LEDGER.jsonl"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    event["paper_order_id"]=str(uuid.uuid4())
    event["ts"]=datetime.now(UTC).isoformat()
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(event,ensure_ascii=False)+"\n")
    return event

def costs_from_ftmo_config(config_path):
    cfg,val=load_ftmo_config(config_path)
    if not cfg or not val["valid"]:
        return {"valid":False,"decision":"BLOCK_INVALID_FTMO_COST_CONFIG","spread":0,"slippage":0,"commission":0}
    return {
        "valid":True,
        "decision":"FTMO_COST_CONFIG_OK",
        "spread":float(cfg.get("spread",0)),
        "slippage":float(cfg.get("slippage",0)),
        "commission":float(cfg.get("commission",0)),
        "config_hash":val.get("hash"),
        "version":cfg.get("version")
    }

def paper_route_order(order, broker="PAPER_INTERNAL", ledger_path="mind_trader/logs/P8.95_PAPER_BROKER_LEDGER.jsonl", spread=0.0, slippage=0.0, commission=0.0, ftmo_config_path=None):
    check=validate_order_payload(order)
    if not check["valid"]:
        return write_paper_broker_ledger({"broker":broker,"decision":"PAPER_ORDER_REJECTED_INVALID_PAYLOAD","payload_check":check,"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE"},ledger_path)

    cost_source={"decision":"MANUAL_COSTS","spread":spread,"slippage":slippage,"commission":commission}

    if ftmo_config_path:
        cost_source=costs_from_ftmo_config(ftmo_config_path)
        if not cost_source["valid"]:
            return write_paper_broker_ledger({"broker":broker,"decision":"PAPER_ORDER_REJECTED_INVALID_COST_CONFIG","cost_source":cost_source,"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE"},ledger_path)
        spread=cost_source["spread"]; slippage=cost_source["slippage"]; commission=cost_source["commission"]

    fill=simulate_fill(order,spread,slippage,commission)
    if not fill["filled"]:
        return write_paper_broker_ledger({"broker":broker,"decision":"PAPER_ORDER_REJECTED_FILL","fill":fill,"cost_source":cost_source,"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE"},ledger_path)

    event={"broker":broker,"order":order,"fill":fill,"cost_source":cost_source,"decision":"PAPER_ORDER_ACCEPTED","order_status":"PAPER_FILLED_SIMULATED","production":"BLOCKED","live":"FORBIDDEN","real_broker_routing":"DISABLED","edge_claim":"NONE"}
    return write_paper_broker_ledger(event,ledger_path)

def paper_broker_summary(ledger_path="mind_trader/logs/P8.95_PAPER_BROKER_LEDGER.jsonl"):
    p=Path(ledger_path)
    rows=[json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []
    return {"broker":"PAPER_INTERNAL","orders":len(rows),"accepted":sum(1 for r in rows if r.get("decision")=="PAPER_ORDER_ACCEPTED"),"rejected":sum(1 for r in rows if r.get("decision")!="PAPER_ORDER_ACCEPTED"),"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE"}
