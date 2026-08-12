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
