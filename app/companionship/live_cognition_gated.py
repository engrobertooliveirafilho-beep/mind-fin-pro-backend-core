import os
from typing import Any, Dict, List


VERSION = "P19P37F_LIVE_COGNITION_GATED"


REQUIRED_LAYERS = [
    "p19p37a_digital_twin_real_shadow",
    "p19p37b_behavior_model_shadow",
    "p19p37c_emotional_continuity_real_shadow",
    "p19p37d_long_term_memory_real_shadow",
    "p19p37e_self_reflection_shadow",
]


OPTIONAL_LAYERS = [
    "p19p36o_relationship_memory_shadow",
    "p19p36p_long_term_goal_shadow",
    "p19p36p_goal_progress_advisor_shadow",
]


def live_cognition_enabled() -> bool:
    return str(os.getenv("P19P37_LIVE_COGNITION_ENABLED", "false")).lower() in {
        "1", "true", "yes", "on"
    }


def build_live_cognition_decision(ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctx = dict(ctx or {})
    enabled = live_cognition_enabled()

    present_required = [k for k in REQUIRED_LAYERS if k in ctx]
    missing_required = [k for k in REQUIRED_LAYERS if k not in ctx]
    present_optional = [k for k in OPTIONAL_LAYERS if k in ctx]

    live_allowed = bool(enabled and not missing_required)

    readiness_score = round(
        (len(present_required) / max(1, len(REQUIRED_LAYERS))) * 0.85
        + (min(len(present_optional), len(OPTIONAL_LAYERS)) / max(1, len(OPTIONAL_LAYERS))) * 0.15,
        4,
    )

    reasons: List[str] = []

    if not enabled:
        reasons.append("feature_flag_off")
    if missing_required:
        reasons.append("missing_required_layers")
    if live_allowed:
        reasons.append("all_required_layers_present_and_flag_enabled")

    return {
        "enabled": enabled,
        "live_allowed": live_allowed,
        "readiness_score": readiness_score,
        "present_required_layers": present_required,
        "missing_required_layers": missing_required,
        "present_optional_layers": present_optional,
        "mode": "LIVE_GATED" if live_allowed else "SHADOW_ONLY",
        "response_impact": "ALLOWED_BY_FEATURE_FLAG" if live_allowed else "NONE",
        "reasons": reasons,
        "version": VERSION,
    }


def attach_live_cognition_shadow(ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctx = dict(ctx or {})
    ctx["p19p37f_live_cognition_decision"] = build_live_cognition_decision(ctx)
    return ctx
