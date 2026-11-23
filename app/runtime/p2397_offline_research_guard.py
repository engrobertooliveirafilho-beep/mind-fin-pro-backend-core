"""Fail-closed guard for P2397 research hypotheses: no runtime promotion."""
from typing import Any

def validate_research_hypothesis(hypothesis: Any, edge_state: Any) -> tuple[bool, str]:
    if not isinstance(hypothesis, dict) or not isinstance(edge_state, dict):
        return False, "INVALID_INPUT"
    if hypothesis.get("paper_only") is not True:
        return False, "PAPER_ONLY_REQUIRED"
    if hypothesis.get("type") not in {"DD_REDUCTION", "SESSION_FOOTPRINT_PRIORITY", "CYCLE_TRANSITION_EXPANSION"}:
        return False, "UNKNOWN_RESEARCH_TYPE"
    if edge_state.get("decision") != "OBSERVE_SCORE":
        return False, "SOURCE_DECISION_MISMATCH"
    if edge_state.get("runtime_promotion") is not False:
        return False, "RUNTIME_PROMOTION_FORBIDDEN"
    return False, "OFFLINE_RESEARCH_ONLY_NO_RUNTIME_AUTHORITY"
