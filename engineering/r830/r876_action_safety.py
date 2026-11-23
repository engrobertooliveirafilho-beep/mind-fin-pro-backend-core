"""Fail-closed, offline gate for the historical STEP 520/525 contracts.
No production hooks, action dispatch, or original-source modification.
"""
import math

BLOCK = {'status': 'blocked', 'executed': False, 'certified_e2e': False}


def assess(action, blocked_actions, *, confirm_threshold=0.5, block_threshold=0.8):
    """Treat any untrusted/missing data or risk as blocked; never execute."""
    if type(action) is not dict or set(action) != {'type', 'risk_hint'}:
        return {**BLOCK, 'reason': 'invalid_action'}
    name, risk = action['type'], action['risk_hint']
    if type(name) is not str or not name or len(name) > 128:
        return {**BLOCK, 'reason': 'invalid_action_name'}
    if type(blocked_actions) not in (list, tuple, frozenset) or not blocked_actions:
        return {**BLOCK, 'reason': 'missing_policy'}
    if any(type(s) is not str or not s for s in blocked_actions):
        return {**BLOCK, 'reason': 'invalid_policy'}
    if type(risk) not in (int, float) or not math.isfinite(risk) or not 0 <= risk <= 1:
        return {**BLOCK, 'reason': 'invalid_risk'}
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in (confirm_threshold, block_threshold)):
        return {**BLOCK, 'reason': 'invalid_thresholds'}
    if not 0 <= confirm_threshold < block_threshold <= 1:
        return {**BLOCK, 'reason': 'invalid_thresholds'}
    if name in blocked_actions:
        return {**BLOCK, 'reason': 'compliance_policy', 'risk_score': risk}
    if risk >= block_threshold:
        return {**BLOCK, 'reason': 'high_risk', 'risk_score': risk}
    if risk >= confirm_threshold:
        return {'status': 'needs_confirmation', 'reason': 'moderate_risk', 'risk_score': risk, 'executed': False, 'certified_e2e': False}
    return {'status': 'eligible_for_external_review_only', 'reason': 'low_risk', 'risk_score': risk, 'executed': False, 'certified_e2e': False}
