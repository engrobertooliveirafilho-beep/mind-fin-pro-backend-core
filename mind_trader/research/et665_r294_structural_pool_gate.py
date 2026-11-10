"""ET665.R294: structural clustering is not temporal diversification certification."""
from collections import Counter

def audit_structural_pool(rows, max_per_family=2, max_total=20):
    items=list(rows)
    problems=[]
    if any(not isinstance(r, dict) for r in items):
        return {"structural_constraints_pass":False,"issues":["MALFORMED_ROW"],"temporal_correlation_measured":False,"causal_walk_forward_verified":False,"runtime_promotion_allowed":False,"status":"QUARANTINE"}
    if not isinstance(max_per_family,int) or isinstance(max_per_family,bool) or max_per_family<1 or not isinstance(max_total,int) or isinstance(max_total,bool) or max_total<1:
        raise ValueError("INVALID_LIMITS")
    if len(items)>max_total:
        problems.append("POOL_CAP_EXCEEDED")
    ids=[r.get("candidate_id") for r in items]
    if any(not isinstance(x,str) for x in ids):
        problems.append("INVALID_CANDIDATE_ID_TYPE")
        ids=[x for x in ids if isinstance(x,str)]
    if any(not x for x in ids) or len(set(ids))!=len(ids):
        problems.append("MISSING_OR_DUPLICATE_CANDIDATE")
    family_keys=[r.get("family_key") for r in items]
    if any(not isinstance(x,str) for x in family_keys):
        problems.append("INVALID_FAMILY_KEY_TYPE")
    families=Counter(x for x in family_keys if isinstance(x,str))
    if any(not family or count>max_per_family for family,count in families.items()):
        problems.append("FAMILY_CAP_EXCEEDED")
    if any(r.get("pool_status")!="DIVERSIFIED_SELECTED" for r in items):
        problems.append("POOL_STATUS_UNVERIFIED")
    if any(r.get("mode") != "PAPER_ONLY" or r.get("real_orders") != "FORBIDDEN" or r.get("ftmo_real") != "FORBIDDEN" or str(r.get("real_execution_allowed")).lower() != "false" or str(r.get("runtime_allowed")).lower() != "false" for r in items):
        problems.append("SAFETY_CONTRACT_INVALID")
    if any(r.get("next_required") != "P2403_CORRELATION_ANALYZER" for r in items):
        problems.append("CORRELATION_GATE_MISSING")
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
