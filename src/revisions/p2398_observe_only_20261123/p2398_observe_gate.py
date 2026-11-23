"""Isolated P2398 PAPER research gate. No order-dispatch capability."""
from collections.abc import Mapping

class GateRejected(ValueError):
    pass

def evaluate(context: Mapping) -> dict:
    if not isinstance(context, Mapping):
        raise GateRejected("context must be a mapping")
    required = {"mode": "PAPER_ONLY", "real_orders": "FORBIDDEN",
                "ftmo_real": "FORBIDDEN", "p2394_decision": "OBSERVE_SCORE",
                "p2395_decision": "OBSERVE_ONLY", "p2396_vote": "OBSERVE_ONLY"}
    for key, expected in required.items():
        if context.get(key) != expected:
            raise GateRejected(f"unsafe or missing {key}")
    if context.get("real_execution_allowed") is not False:
        raise GateRejected("real execution not explicitly denied")
    if context.get("runtime_modification_allowed") is not False:
        raise GateRejected("runtime modification not explicitly denied")
    if type(context.get("operational_members")) is not int or context["operational_members"] != 0:
        raise GateRejected("operational quorum mismatch")
    if type(context.get("quorum_required")) is not int or context["quorum_required"] < 2:
        raise GateRejected("invalid quorum")
    return {"decision": "OBSERVE_ONLY", "runtime_promotion": False,
            "order_dispatch": False, "research_only": True}
