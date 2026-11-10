"""ET665.R294: structural clustering is not temporal diversification certification."""
from collections import Counter

def audit_structural_pool(rows, max_per_family=2, max_total=20):
    items=list(rows)
    problems=[]
    if len(items)>max_total:
        problems.append("POOL_CAP_EXCEEDED")
    ids=[r.get("candidate_id") for r in items]
    if any(not x for x in ids) or len(set(ids))!=len(ids):
        problems.append("MISSING_OR_DUPLICATE_CANDIDATE")
    families=Counter(r.get("family_key") for r in items)
    if any(not family or count>max_per_family for family,count in families.items()):
        problems.append("FAMILY_CAP_EXCEEDED")
    if any(r.get("pool_status")!="DIVERSIFIED_SELECTED" for r in items):
        problems.append("POOL_STATUS_UNVERIFIED")
    if not items:
        problems.append("EMPTY_POOL")
    return {
        "structural_constraints_pass":not problems,
        "issues":problems,
        "temporal_correlation_measured":False,
        "causal_walk_forward_verified":False,
        "runtime_promotion_allowed":False,
        "status":"QUARANTINE",
    }
