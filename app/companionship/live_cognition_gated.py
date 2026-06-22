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


def _rank_items(items):
    values = list(items or [])
    ranked = []

    for idx,item in enumerate(values):
        ranked.append({
            "rank": idx + 1,
            "value": item,
        })

    return ranked


def build_p19p46_live_cognition_evolution(
    *,
    contexts=None,
    goals=None,
    memories=None,
    reflections=None,
):
    """
    P19P46

    Shadow-only live cognition layer.
    """

    context_items = list(contexts or [])
    goal_items = list(goals or [])
    memory_items = list(memories or [])
    reflection_items = list(reflections or [])

    context_ranking = _rank_items(context_items)
    goal_ranking = _rank_items(goal_items)
    memory_ranking = _rank_items(memory_items)
    reflection_ranking = _rank_items(reflection_items)

    priority_engine = {
        "context_priority_count": len(context_ranking),
        "goal_priority_count": len(goal_ranking),
        "memory_priority_count": len(memory_ranking),
        "reflection_priority_count": len(reflection_ranking),
    }

    decision_engine = {
        "recommended_focus": (
            "goal"
            if len(goal_ranking) >= len(context_ranking)
            else "context"
        ),
        "signal_count": (
            len(context_items)
            + len(goal_items)
            + len(memory_items)
            + len(reflection_items)
        ),
    }

    return {
        "program": "P19P46",
        "mode": "SHADOW_ONLY",
        "live_cognition_evolution": {
            "decision_engine": decision_engine,
            "priority_engine": priority_engine,
            "context_ranking": context_ranking,
            "goal_ranking": goal_ranking,
            "memory_ranking": memory_ranking,
            "reflection_ranking": reflection_ranking,
        },
        "safety": {
            "runtime_mutation": False,
            "response_mutation": False,
            "rollbackable": True,
            "canary_ready": True,
        },
    }

