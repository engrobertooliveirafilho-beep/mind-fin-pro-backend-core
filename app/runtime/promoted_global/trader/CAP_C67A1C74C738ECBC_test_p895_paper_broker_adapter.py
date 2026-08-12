from pathlib import Path
from mind_trader.app.execution.paper_broker_adapter import paper_route_order, paper_broker_summary

def order():
    return {"symbol":"WIN","side":"BUY","entry":100,"stop":98,"target":104,"risk_amount":500,"strategy_id":"S1"}

def test_paper_route_order_accepts_valid_order(tmp_path):
    r=paper_route_order(order(),ledger_path=str(tmp_path/"ledger.jsonl"))
    assert r["decision"]=="PAPER_ORDER_ACCEPTED"
    assert r["order_status"]=="PAPER_FILLED_SIMULATED"
    assert r["real_broker_routing"]=="DISABLED"
    assert r["production"]=="BLOCKED"

def test_paper_route_order_rejects_invalid_payload(tmp_path):
    r=paper_route_order({"symbol":"WIN"},ledger_path=str(tmp_path/"ledger.jsonl"))
    assert r["decision"]=="PAPER_ORDER_REJECTED_INVALID_PAYLOAD"
    assert r["live"]=="FORBIDDEN"

def test_paper_broker_summary(tmp_path):
    ledger=tmp_path/"ledger.jsonl"
    paper_route_order(order(),ledger_path=str(ledger))
    paper_route_order({"symbol":"WIN"},ledger_path=str(ledger))
    s=paper_broker_summary(str(ledger))
    assert s["orders"]==2
    assert s["accepted"]==1
    assert s["rejected"]==1
    assert s["edge_claim"]=="NONE"

def test_paper_broker_ledger_written(tmp_path):
    ledger=tmp_path/"ledger.jsonl"
    paper_route_order(order(),ledger_path=str(ledger))
    assert Path(ledger).exists()
