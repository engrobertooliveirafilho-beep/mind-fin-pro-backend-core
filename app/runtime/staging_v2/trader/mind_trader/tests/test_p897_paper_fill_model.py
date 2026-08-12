from mind_trader.app.execution.paper_fill_model import simulate_fill
from mind_trader.app.execution.paper_broker_adapter import paper_route_order

def order():
    return {"symbol":"WIN","side":"BUY","entry":100,"stop":98,"target":104,"risk_amount":500,"strategy_id":"S1"}

def test_simulate_buy_fill_with_costs():
    r=simulate_fill(order(),spread=0.2,slippage=0.1,commission=1)
    assert r["filled"] is True
    assert round(r["fill_price"], 10)==100.2
    assert r["commission"]==1
    assert r["production"]=="BLOCKED"

def test_simulate_fill_rejects_invalid_side():
    o=order(); o["side"]="BAD"
    r=simulate_fill(o)
    assert r["filled"] is False
    assert r["decision"]=="FILL_REJECT_INVALID_SIDE"

def test_paper_route_order_has_fill(tmp_path):
    r=paper_route_order(order(),ledger_path=str(tmp_path/"ledger.jsonl"),spread=0.2,slippage=0.1,commission=1)
    assert r["decision"]=="PAPER_ORDER_ACCEPTED"
    assert r["fill"]["decision"]=="FILL_SIMULATED"
    assert r["real_broker_routing"]=="DISABLED"

def test_paper_route_order_rejects_bad_fill(tmp_path):
    o=order(); o["side"]="BAD"
    r=paper_route_order(o,ledger_path=str(tmp_path/"ledger.jsonl"))
    assert r["decision"]=="PAPER_ORDER_REJECTED_FILL"

