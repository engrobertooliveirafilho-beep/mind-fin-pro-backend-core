from pathlib import Path
from mind_trader.app.execution.safe_broker_adapter import broker_adapter_contract, validate_order_payload, blocked_send_order

def order():
    return {"symbol":"WIN","side":"BUY","entry":100,"stop":98,"target":104,"risk_amount":500,"strategy_id":"S1"}

def test_broker_contract_mt5():
    r=broker_adapter_contract("MT5")
    assert r["real_send_order"]=="FORBIDDEN"
    assert r["production"]=="BLOCKED"

def test_broker_contract_unsupported():
    r=broker_adapter_contract("BAD")
    assert r["decision"]=="BROKER_UNSUPPORTED"

def test_validate_order_payload():
    r=validate_order_payload(order())
    assert r["valid"] is True

def test_blocked_send_order():
    r=blocked_send_order("MT5",order())
    assert r["decision"]=="FORCE_BLOCK_BROKER_SEND_ORDER"
    assert r["live_lock"]["decision"]=="FORCE_BLOCK_LIVE_OR_PRODUCTION"
    assert r["live"]=="FORBIDDEN"

def test_broker_adapter_report_written():
    blocked_send_order("PROFIT",order())
    assert Path("mind_trader/reports/P8.94_safe_broker_adapter.json").exists()
