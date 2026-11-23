"""Offline integration: authority preflight must precede any PAPER risk decision.

No broker import, network call, or order execution.
"""
from paper_risk_gate import authorize_paper_order


def evaluate_paper_intent(order, state, *, preflight, integration):
    """Deny by default; caller-supplied reports are untrusted unless both gates pass."""
    denied = {"approved": False, "mode": "PAPER_ONLY", "real_orders_authorized": False}
    if not isinstance(preflight, dict) or not isinstance(integration, dict):
        return {**denied, "reason": "MISSING_GATE_EVIDENCE"}
    if (preflight.get("status") != "PAPER_DISPATCH_CERTIFIED"
            or integration.get("status") != "PAPER_DISPATCH_CERTIFIED"
            or preflight.get("missing_phases")
            or preflight.get("findings")
            or integration.get("canonical_runtime_verified") is not True
            or integration.get("s20_s21_join_verified") is not True
            or integration.get("long_run_certified") is not True):
        return {**denied, "reason": "INTEGRATION_NOT_CERTIFIED"}
    # Even if the integration reports are positive, the risk guard remains mandatory.
    return authorize_paper_order(order, state)
