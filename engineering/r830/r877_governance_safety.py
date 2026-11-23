"""Offline fail-closed STEP 529/543 governance and evolution review gate."""
import math

BLOCK = {'status': 'blocked', 'human_review_authorized': False, 'executed': False, 'e2e_certified': False}


def review(proposal, personas):
    if type(proposal) is not dict or set(proposal) != {'step_id', 'title', 'risk_score', 'alignment_score', 'redundancy_score'}:
        return {**BLOCK, 'reason': 'invalid_proposal'}
    if type(proposal['step_id']) is not int or proposal['step_id'] < 1 or type(proposal['title']) is not str or not proposal['title'].strip() or len(proposal['title']) > 200:
        return {**BLOCK, 'reason': 'invalid_identity'}
    if type(personas) not in (list, tuple) or len(personas) < 3 or len(personas) > 20 or any(type(p) is not str or not p for p in personas) or len(set(personas)) != len(personas):
        return {**BLOCK, 'reason': 'invalid_board'}
    required = {'legal', 'risk', 'ethics'}
    if not required.issubset(personas):
        return {**BLOCK, 'reason': 'incomplete_board'}
    for field in ('risk_score', 'alignment_score', 'redundancy_score'):
        val = proposal[field]
        if type(val) not in (int, float) or not math.isfinite(val) or not 0 <= val <= 1:
            return {**BLOCK, 'reason': 'invalid_' + field}
    if proposal['risk_score'] > 0.7:
        return {**BLOCK, 'reason': 'high_risk'}
    if proposal['alignment_score'] < 0.6:
        return {**BLOCK, 'reason': 'low_alignment'}
    if proposal['redundancy_score'] > 0.7:
        return {**BLOCK, 'reason': 'high_redundancy'}
    if proposal['risk_score'] >= 0.4:
        return {**BLOCK, 'reason': 'board_abstains'}
    return {'status': 'candidate_for_human_review_only', 'step_id': proposal['step_id'],
            'human_review_authorized': False, 'executed': False, 'e2e_certified': False}
