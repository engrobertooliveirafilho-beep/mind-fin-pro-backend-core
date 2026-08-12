import json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.security.institutional_live_lock import institutional_live_lock

SUPPORTED_BROKERS={"MT5","PROFIT"}

def broker_adapter_contract(broker):
    if broker not in SUPPORTED_BROKERS:
        return {"decision":"BROKER_UNSUPPORTED","broker":broker,"production":"BLOCKED","edge_claim":"NONE"}
    return {
        "broker":broker,
        "contract":"P8.94_SAFE_BROKER_ADAPTER_CONTRACT",
        "methods":["validate_order","paper_route","blocked_send_order"],
        "real_send_order":"FORBIDDEN",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

def validate_order_payload(order):
    required=["symbol","side","entry","stop","target","risk_amount","strategy_id"]
    missing=[k for k in required if k not in order or order[k] in [None,""]]
    return {"valid":not missing,"missing":missing,"decision":"ORDER_PAYLOAD_OK" if not missing else "ORDER_PAYLOAD_INVALID"}

def blocked_send_order(broker, order):
    contract=broker_adapter_contract(broker)
    if contract.get("decision")=="BROKER_UNSUPPORTED":
        return contract
    payload_check=validate_order_payload(order)
    lock=institutional_live_lock("BROKER_SEND_ORDER",{"broker":broker,"order":order})
    report={
        "adapter":"P8.94_SAFE_BROKER_ADAPTER",
        "created_at":datetime.now(UTC).isoformat(),
        "broker":broker,
        "payload_check":payload_check,
        "live_lock":lock,
        "decision":"FORCE_BLOCK_BROKER_SEND_ORDER",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.94_safe_broker_adapter.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
