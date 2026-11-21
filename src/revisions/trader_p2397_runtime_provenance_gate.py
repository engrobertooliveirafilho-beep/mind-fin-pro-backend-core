"""P2397 runtime provenance gate: deny any operational authorization without independently verified lineage."""
from __future__ import annotations
import math


def assess_runtime(score: dict, router: dict, ensemble: dict, policy: dict) -> dict:
    blocked = {"allowed": False, "decision": "OBSERVE_ONLY", "mode": "PAPER_ONLY",
               "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"}
    if not all(isinstance(x, dict) for x in (score, router, ensemble, policy)):
        return blocked
    if policy.get("mode") != "PAPER_ONLY" or policy.get("real_orders") != "FORBIDDEN":
        return blocked
    if policy.get("ftmo_real") != "FORBIDDEN" or policy.get("runtime_modification_allowed") is not False:
        return blocked
    if policy.get("broker_execution_allowed") is not False or policy.get("ftmo_real_allowed") is not False:
        return blocked
    if score.get("decision") != "PROMOTE_SCORE":
        return blocked
    try:
        value = score["final_score"]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return blocked
        if not math.isfinite(value) or value < 70:
            return blocked
    except (KeyError, TypeError, ValueError):
        return blocked
    if router.get("allowed") is not True or router.get("route") != "PAPER_OPERATIONAL":
        return blocked
    if ensemble.get("allowed") is not True or ensemble.get("vote") != "PAPER_OPERATIONAL":
        return blocked
    members, quorum = ensemble.get("operational_members"), ensemble.get("quorum")
    if type(members) is not int or type(quorum) is not int or quorum < 2 or members < quorum:
        return blocked
    # No trusted causal provenance token is currently available; fail closed.
    return blocked
