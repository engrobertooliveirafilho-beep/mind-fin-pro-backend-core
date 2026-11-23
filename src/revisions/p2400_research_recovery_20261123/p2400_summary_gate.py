"""Read-only fail-closed P2400 historical research summary validator."""
from collections.abc import Mapping

def validate_p2400(summary, policy):
    if not isinstance(summary, Mapping) or not isinstance(policy, Mapping):
        return False
    expected = {"mission":"P2400_RESEARCH_SPACE_EXPANSION","mode":"PAPER_ONLY",
                "real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
                "generated_candidates":7500,"exported_candidates":500,
                "context_families":45,"runtime_promotion_allowed":False,
                "research_allowed":True,"real_execution_allowed":False,
                "next_required":"P2401_MULTI_EDGE_WALK_FORWARD_DD_FILTER"}
    for key,value in expected.items():
        if summary.get(key) != value or type(summary.get(key)) is not type(value):
            return False
    required = {"mission":"P2400_RESEARCH_SPACE_EXPANSION","mode":"PAPER_ONLY",
                "real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
                "runtime_allowed":False,"research_only":True,
                "validation_required_next":"P2401_MULTI_EDGE_WALK_FORWARD_DD_FILTER"}
    return all(policy.get(k) == v and type(policy.get(k)) is type(v)
               for k,v in required.items())
