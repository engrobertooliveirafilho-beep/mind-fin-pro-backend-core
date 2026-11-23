"""Read-only verification of historical P2393 provenance. No orders, no writes."""
import hashlib
import json

def verify_p2393(p2392: dict, p2393: dict) -> tuple[bool, str]:
    if not isinstance(p2392, dict) or not isinstance(p2393, dict):
        return False, "INPUT_NOT_OBJECT"
    for doc in (p2392, p2393):
        if doc.get("mode") != "PAPER_ONLY" or doc.get("real_orders") != "FORBIDDEN" or doc.get("ftmo_real") != "FORBIDDEN":
            return False, "EXECUTION_MODE_FORBIDDEN"
        if doc.get("real_execution_allowed") is not False or doc.get("paper_stack_modified") is not False:
            return False, "PRODUCTION_MUTATION_FORBIDDEN"
    best = p2392.get("best_promoted")
    cluster = p2393.get("best_cluster")
    if not isinstance(best, dict) or not isinstance(cluster, dict):
        return False, "MISSING_EDGE_OR_CLUSTER"
    if p2392.get("promoted") != 1 or p2393.get("clusters_created") != 1:
        return False, "COUNT_MISMATCH"
    key = "|".join(str(best.get(k, "")) for k in ("dimensions", "key", "direction"))
    expected_id = "P2393_CLUSTER_" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:12].upper()
    if cluster.get("cluster_id") != expected_id:
        return False, "CLUSTER_ID_MISMATCH"
    if cluster.get("source_candidate_id") != best.get("candidate_id"):
        return False, "CANDIDATE_ID_MISMATCH"
    for field in ("dimensions", "key", "direction", "samples", "passed_windows", "pf", "winrate", "expectancy", "max_dd_r", "net_r"):
        if cluster.get(field) != best.get(field):
            return False, "CLUSTER_SOURCE_MISMATCH:" + field
    if cluster.get("decision") != "PROMOTE_CLUSTER" or cluster.get("members") != 1:
        return False, "CLUSTER_STRUCTURE_INVALID"
    return True, "HISTORICAL_DOCUMENTS_CONSISTENT_NOT_E2E_CERTIFIED"
