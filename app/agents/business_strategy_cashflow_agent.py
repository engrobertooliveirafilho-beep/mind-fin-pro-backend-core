"""Real deterministic cashflow agent. PAPER-only, no external effects."""
from decimal import Decimal, InvalidOperation
import hashlib
import json

AGENT_ID = "business.strategy_cashflow_agent"
FIELDS = ("revenue", "fixed_costs", "variable_costs", "cash_balance")

def _amount(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError("invalid amount type")
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid decimal") from exc
    if not d.is_finite() or d < 0 or d.as_tuple().exponent < -2:
        raise ValueError("invalid amount")
    return d

def _sha(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def describe_capabilities():
    return {"agent_id": AGENT_ID, "components": ["monthly_cashflow"], "mode": "paper_only"}

def run_dry(payload=None):
    if not isinstance(payload, dict) or set(payload) != set(FIELDS) | {"component", "input_sha256"}:
        raise ValueError("invalid payload schema")
    if payload["component"] != "monthly_cashflow":
        raise ValueError("unsupported component")
    source = {k: payload[k] for k in ("component",) + FIELDS}
    if not isinstance(payload["input_sha256"], str) or payload["input_sha256"] != _sha(source):
        raise ValueError("input hash mismatch")
    vals = {key: _amount(payload[key]) for key in FIELDS}
    net = vals["revenue"] - vals["fixed_costs"] - vals["variable_costs"]
    burn = max(-net, Decimal("0"))
    runway = None if burn == 0 else (vals["cash_balance"] / burn).quantize(Decimal("0.01"))
    output = {
        "net_cashflow": str(net.quantize(Decimal("0.01"))),
        "monthly_burn": str(burn.quantize(Decimal("0.01"))),
        "runway_months": str(runway) if runway is not None else None,
    }
    return {
        "agent_id": AGENT_ID,
        "status": "processed",
        "mode": "paper_only",
        "component": "monthly_cashflow",
        "input_sha256": payload["input_sha256"],
        "output": output,
        "output_sha256": _sha(output),
        "processed_items": len(FIELDS),
        "real_orders": "FORBIDDEN",
        "promotion_authorized": False,
    }
