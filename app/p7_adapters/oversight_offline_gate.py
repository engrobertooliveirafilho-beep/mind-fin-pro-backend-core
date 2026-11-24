from math import isfinite

def authorize(payload):
    """Authorize offline analysis only; never authorize external execution."""
    if payload.execution_mode != 'offline_analysis':
        return False
    if payload.candidate_action not in ('inspect', 'plan'):
        return False
    if payload.risk_flags or payload.policy_constraints:
        return False
    c = payload.confidence
    return c is not None and isfinite(c) and 0.9 <= c <= 1.0
