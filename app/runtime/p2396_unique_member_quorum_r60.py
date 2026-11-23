"""R60: prevent duplicate-member quorum inflation in PAPER ensemble."""
def validate_unique_quorum(votes, quorum=2):
    if type(quorum) is not int or quorum < 2:
        return False, "INVALID_QUORUM"
    if not isinstance(votes, list) or not votes:
        return False, "NO_VOTES"
    seen = set()
    count = 0
    for vote in votes:
        if not isinstance(vote, dict):
            return False, "VOTE_NOT_OBJECT"
        if vote.get("mode") != "PAPER_ONLY" or vote.get("real_orders") != "FORBIDDEN" or vote.get("ftmo_real") != "FORBIDDEN":
            return False, "EXECUTION_MODE_FORBIDDEN"
        member = vote.get("member_id")
        if not isinstance(member, str) or not member.strip():
            return False, "MEMBER_ID_REQUIRED"
        if member in seen:
            return False, "DUPLICATE_MEMBER"
        seen.add(member)
        if vote.get("allowed") is True and vote.get("edge_score_decision") == "PROMOTE_SCORE" and vote.get("route") == "PAPER_OPERATIONAL":
            count += 1
    if count < quorum:
        return False, "INSUFFICIENT_OPERATIONAL_QUORUM"
    return False, "INDEPENDENT_ENSEMBLE_EVIDENCE_REQUIRED"
