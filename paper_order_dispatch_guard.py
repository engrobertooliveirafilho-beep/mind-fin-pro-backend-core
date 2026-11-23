"""Fail-closed offline dispatch gate; no broker or network integration."""
from paper_risk_gate import authorize_paper_order


def evaluate_paper_intent(order, state, *, preflight=None, integration=None):
    denied = {'approved': False, 'mode': 'PAPER_ONLY', 'real_orders_authorized': False}
    # Caller-supplied dictionaries are not proof of authority. Recompute the
    # historical R6 gate from its original, read-only local evidence.
    try:
        from adapter import preflight as local_preflight
        from integration_gate import evaluate as local_integration
        actual_preflight = local_preflight()
        actual_integration = local_integration()
    except (ImportError, OSError, ValueError, KeyError, TypeError):
        return {**denied, 'reason': 'CANONICAL_GATE_UNAVAILABLE'}
    if (actual_preflight.get('status') != 'PAPER_DISPATCH_CERTIFIED'
            or actual_integration.get('status') != 'PAPER_DISPATCH_CERTIFIED'
            or actual_preflight.get('missing_phases')
            or actual_preflight.get('findings')
            or actual_integration.get('canonical_runtime_verified') is not True
            or actual_integration.get('s20_s21_join_verified') is not True
            or actual_integration.get('long_run_certified') is not True):
        return {**denied, 'reason': 'INTEGRATION_NOT_CERTIFIED'}
    return authorize_paper_order(order, state)
