from .oversight_contracts import OversightInput, OversightDecision


def review_or_guard(payload: OversightInput) -> OversightDecision:
    """
    P7 isolated shadow adapter.

    Rules:
    - Does not block runtime.
    - Does not mutate memory.
    - Does not rewrite response.
    - Emits auditable decision only.
    """
    risk_level = "LOW" if not payload.risk_flags else "MEDIUM"

    return OversightDecision(
        decision="REVIEW" if payload.risk_flags else "ALLOW",
        allowed=True,
        reason="shadow_mode_audit_only",
        risk_level=risk_level,
        required_revision=None,
        audit_trace=[
            "p7_oversight_shadow_adapter",
            "no_runtime_mutation",
            "no_blocking_enforcement",
        ],
    )
