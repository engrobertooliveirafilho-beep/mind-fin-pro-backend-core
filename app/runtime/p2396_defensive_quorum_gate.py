"""P2396 ensemble defensive quorum gate: no real orders, no unverified promotion."""
from typing import Any

def validate_ensemble_vote(votes: Any, quorum: int = 2) -> tuple[bool, str]:
    if type(quorum) is not int or quorum < 2:
        return False, "INVALID_QUORUM"
    if not isinstance(votes, list) or not votes:
        return False, "NO_VOTES"
    operational = 0
    for vote in votes:
        if not isinstance(vote, dict):
            return False, "VOTE_NOT_OBJECT"
        if vote.get("mode") != "PAPER_ONLY" or vote.get("real_orders") != "FORBIDDEN" or vote.get("ftmo_real") != "FORBIDDEN":
            return False, "EXECUTION_MODE_FORBIDDEN"
        if vote.get("edge_score_decision") != "PROMOTE_SCORE" or vote.get("route") != "PAPER_OPERATIONAL" or vote.get("allowed") is not True:
            continue
        operational += 1
    if operational < quorum:
        return False, "INSUFFICIENT_OPERATIONAL_QUORUM"
    return False, "INDEPENDENT_ENSEMBLE_EVIDENCE_REQUIRED"
