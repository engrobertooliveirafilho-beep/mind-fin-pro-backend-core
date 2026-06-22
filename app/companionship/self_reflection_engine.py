from typing import Any, Dict

VERSION = "P19P37E_SELF_REFLECTION"

def build_self_reflection(ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctx = dict(ctx or {})
    known = []
    unknown = []
    risks = []

    if ctx.get("p19p37a_digital_twin_real_shadow"): known.append("digital_twin_profile")
    else: unknown.append("digital_twin_profile")

    if ctx.get("p19p37d_long_term_memory_real_shadow"): known.append("long_term_memory")
    else: unknown.append("long_term_memory")

    if ctx.get("p19p37c_emotional_continuity_real_shadow"): known.append("emotional_continuity")
    else: unknown.append("emotional_continuity")

    if not known:
        risks.append("insufficient_context")

    return {
        "known": known,
        "unknown": unknown,
        "risks": risks,
        "confidence": "HIGH" if len(known) >= 3 else "MEDIUM" if known else "LOW",
        "mode": "SHADOW_ONLY",
        "version": VERSION,
    }

def attach_self_reflection_shadow(ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctx = dict(ctx or {})
    ctx["p19p37e_self_reflection_shadow"] = build_self_reflection(ctx)
    return ctx


from datetime import datetime, timezone


def _score_text_quality(text):
    if not isinstance(text, str) or not text.strip():
        return 0.0

    length = len(text.strip())
    score = 0.0

    if length >= 20:
        score += 0.25
    if length <= 1200:
        score += 0.25
    if any(mark in text for mark in [".", "!", "?", ":"]):
        score += 0.20
    if not any(bad in text.lower() for bad in ["placeholder", "lorem ipsum", "todo"]):
        score += 0.30

    return min(1.0, round(score, 4))


def _score_collection_usefulness(items):
    values = list(items or [])

    if not values:
        return 0.0

    non_empty = sum(1 for item in values if str(item).strip())
    uniqueness = len({str(item).strip().lower() for item in values if str(item).strip()})

    score = (non_empty / max(1, len(values))) * 0.6
    score += min(1.0, uniqueness / max(1, len(values))) * 0.4

    return min(1.0, round(score, 4))


def build_p19p45_self_reflection_evolution(
    *,
    response_text=None,
    memory_items=None,
    cognitive_context=None,
    prior_reflections=None,
):
    """
    P19P45 Self Reflection Evolution.

    Shadow-only reflection layer.
    Does not mutate runtime.
    Does not mutate outbound responses.
    """

    memory_values = list(memory_items or [])
    prior_values = list(prior_reflections or [])
    cognition = dict(cognitive_context or {})

    response_quality = _score_text_quality(response_text)
    memory_usefulness = _score_collection_usefulness(memory_values)

    cognition_signal_count = len(cognition.keys())
    cognition_usefulness = min(
        1.0,
        round(cognition_signal_count / 8.0, 4),
    )

    ledger_entry = {
        "program": "P19P45",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "SHADOW_ONLY",
        "response_quality_score": response_quality,
        "memory_usefulness_score": memory_usefulness,
        "cognition_usefulness_score": cognition_usefulness,
        "prior_reflection_count": len(prior_values),
    }

    return {
        "program": "P19P45",
        "mode": "SHADOW_ONLY",
        "self_reflection_evolution": {
            "response_quality_scoring": {
                "score": response_quality,
            },
            "memory_usefulness_scoring": {
                "score": memory_usefulness,
                "memory_item_count": len(memory_values),
            },
            "cognition_usefulness_scoring": {
                "score": cognition_usefulness,
                "cognitive_signal_count": cognition_signal_count,
            },
            "reflection_ledger": [*prior_values, ledger_entry],
        },
        "safety": {
            "runtime_mutation": False,
            "response_mutation": False,
            "rollbackable": True,
            "canary_ready": True,
        },
    }

