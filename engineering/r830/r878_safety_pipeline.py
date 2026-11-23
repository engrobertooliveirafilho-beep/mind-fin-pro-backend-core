"""Deterministic offline composition of R876 action and R877 governance gates."""
from r876_action_safety import assess
from r877_governance_safety import review


def inspect(action, blocked_actions, proposal, personas):
    blocked = {'status': 'blocked', 'executed': False, 'e2e_certified': False}
    first = assess(action, blocked_actions)
    if first['status'] != 'eligible_for_external_review_only':
        return {**blocked, 'reason': 'action_' + first.get('reason', 'blocked')}
    second = review(proposal, personas)
    if second['status'] != 'candidate_for_human_review_only':
        return {**blocked, 'reason': 'governance_' + second.get('reason', 'blocked')}
    return {'status': 'dual_review_candidate_only', 'action': action['type'],
            'step_id': proposal['step_id'], 'executed': False, 'e2e_certified': False,
            'human_approval_required': True, 'dispatch_authorized': False}
