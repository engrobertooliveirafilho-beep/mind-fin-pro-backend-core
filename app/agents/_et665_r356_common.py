"""Deterministic offline analysis primitives; no side effects or broker access."""
import hashlib
import json

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def validate(payload):
    if not isinstance(payload,dict) or set(payload)!={"component","revenue","fixed_costs","variable_costs","cash_balance","input_sha256"}:
        raise ValueError("invalid input schema")
    if payload["component"]!="monthly_cashflow":
        raise ValueError("unsupported component")
    source={k:v for k,v in payload.items() if k!="input_sha256"}
    if payload["input_sha256"]!=digest(source):
        raise ValueError("input hash mismatch")
    from decimal import Decimal,InvalidOperation
    amounts={}
    for k in ("revenue","fixed_costs","variable_costs","cash_balance"):
        v=payload[k]
        if isinstance(v,bool) or not isinstance(v,(str,int)):
            raise ValueError("invalid monetary type")
        try:
            d=Decimal(str(v))
        except (InvalidOperation,ValueError) as exc:
            raise ValueError("invalid amount") from exc
        if not d.is_finite() or d<0 or d.as_tuple().exponent < -2:
            raise ValueError("invalid amount")
        amounts[k]=d
    return amounts

def attest(agent_id,payload,output):
    return {"agent_id":agent_id,"status":"processed","mode":"paper_only",
            "component":"monthly_cashflow","input_sha256":payload["input_sha256"],
            "output":output,"output_sha256":digest(output),"processed_items":4,
            "real_orders":"FORBIDDEN","promotion_authorized":False}
