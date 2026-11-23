"""P2402 evidence safety gate: structural diversity is not measured market correlation."""
from collections.abc import Mapping

def validate_p2402(summary):
    if not isinstance(summary,Mapping): return False
    fields={"mission":"P2402_CONTEXT_DIVERSITY_CLUSTERING","mode":"PAPER_ONLY",
        "real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
        "promoted_input":34,"structural_clusters":29,"representatives":29,
        "selected_pool":20,"families":18,"max_per_family":2,
        "runtime_promotion_allowed":False,"real_execution_allowed":False,
        "next_required":"P2403_CORRELATION_ANALYZER"}
    if not all(summary.get(k)==v and type(summary.get(k)) is type(v) for k,v in fields.items()):
        return False
    return summary.get("correlation")=="NOT_MEASURED_YET"

def certification(summary):
    return {"structural_research_only":validate_p2402(summary),
            "performance_certified":False,"correlation_certified":False,
            "runtime_promotion_allowed":False}
