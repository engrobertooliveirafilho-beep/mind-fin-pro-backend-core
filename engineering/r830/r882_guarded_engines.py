"""R882: fail-closed facade for STEP 532/533/540/542 legacy engines.
No original mutations; no approval or treaty acceptance from unverified inputs.
"""
from r879_knowledge_treaty_ethics import validate_knowledge, validate_treaty, validate_ethics


def promote(builder, key, version, payload, evidence):
    """Only verified external authorization can reach the original promotion method."""
    result = validate_knowledge(key, version, payload, promotion=True,
                                attested=type(evidence) is dict and evidence.get('verified') is True)
    if result.get('status') != 'review_candidate_only':
        return {'status': 'blocked', 'reason': result.get('reason', 'gate_failed'), 'executed': False}
    # R879's candidate status explicitly disallows promotion, even if attested.
    return {'status': 'blocked', 'reason': 'external_authorization_not_implemented', 'executed': False}


def negotiate(protocol, parties, proposal):
    result = validate_treaty(parties, proposal)
    if result.get('status') != 'treaty_review_only':
        return {'status': 'blocked', 'reason': result.get('reason', 'gate_failed'), 'executed': False}
    # R879 never grants treaty acceptance. Preserve this semantic.
    return {'status': 'review_only', 'accepted': False, 'executed': False}


def approve(board, item_id, reviewer, evidence):
    result = validate_ethics(item_id, reviewer, 'approve', evidence)
    if result.get('status') != 'ethical_review_candidate_only':
        return {'status': 'blocked', 'reason': result.get('reason', 'gate_failed'), 'executed': False}
    return {'status': 'review_only', 'approval_authorized': False, 'executed': False}
