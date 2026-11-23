"""Fail-closed P2395 routing guard based on the historical P2394 decision."""
from typing import Any, Mapping, Tuple

def validate_p2395_routing(p2394: Mapping[str, Any], request: Mapping[str, Any]) -> Tuple[bool, str]:
    if not isinstance(p2394, dict) or not isinstance(request, dict):
        return False, "INVALID_INPUT"
    if p2394.get("decision") != "PROMOTE_SCORE":
        return False, "P2394_NOT_PROMOTED_OBSERVE_ONLY"
    if request.get("mode") != "PAPER_ONLY" or request.get("real_orders") != "FORBIDDEN" or request.get("ftmo_real") != "FORBIDDEN":
        return False, "EXECUTION_MODE_FORBIDDEN"
    if request.get("cluster_id") != p2394.get("cluster_id"):
        return False, "CLUSTER_LINEAGE_MISMATCH"
    return False, "INDEPENDENT_ROUTER_INTEGRATION_NOT_CERTIFIED"
