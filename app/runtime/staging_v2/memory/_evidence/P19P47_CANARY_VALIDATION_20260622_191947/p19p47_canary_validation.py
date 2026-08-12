import json
from datetime import datetime, timezone

from app.companionship.cognitive_context_builder import build_cognitive_context
from app.companionship.safe_recovery_adapter import attach_p19p40_cognitive_context_shadow
from app.runtime.cognitive_pipeline import attach_p19p41_cognitive_context_shadow
from app.api.whatsapp import attach_p19p42_whatsapp_cognitive_context_shadow
from app.companionship.digital_twin_real import build_p19p43_digital_twin_evolution
from app.companionship.behavior_modeling import build_p19p44_behavior_modeling_evolution
from app.companionship.self_reflection_engine import build_p19p45_self_reflection_evolution
from app.companionship.live_cognition_gated import build_p19p46_live_cognition_evolution


def main():
    flags = {
        "P19P41_COGNITIVE_CONTEXT_ENABLED": False,
        "P19P42_WHATSAPP_COGNITIVE_CONTEXT_ENABLED": False,
    }

    digital_twin = build_p19p43_digital_twin_evolution(
        user_profile={"style": "direct"},
        interests=["study", "fitness"],
        goals=["launch"],
        relationship_memory={"trust": 0.9},
        behavior_model={"short_followups": True},
    )

    behavior = build_p19p44_behavior_modeling_evolution(
        interactions=["prossiga", "como faço?"],
        responses=["direto, sem enrolação"],
        topics=["eldora", "runtime", "eldora"],
        engagement_events=["continue"],
    )

    reflection = build_p19p45_self_reflection_evolution(
        response_text="Resposta direta e útil.",
        memory_items=["preferência por respostas diretas"],
        cognitive_context={"digital_twin": digital_twin, "behavior": behavior},
    )

    live = build_p19p46_live_cognition_evolution(
        contexts=["runtime", "whatsapp"],
        goals=["stability"],
        memories=["direct_style"],
        reflections=["quality_ok"],
    )

    ctx = build_cognitive_context(
        user_id="canary-user",
        relationship_memory={"trust": 0.9},
        goal_tracking={"active_goals": 1},
        digital_twin=digital_twin,
        behavior_modeling=behavior,
        emotional_continuity={"status": "stable"},
        long_term_memory={"items": 1},
        self_reflection=reflection,
        live_cognition=live,
        source_context={"canary": True},
        feature_flags=flags,
    )

    propagated = attach_p19p40_cognitive_context_shadow(ctx, user_id="canary-user")
    propagated = attach_p19p41_cognitive_context_shadow(propagated, flags)
    propagated = attach_p19p42_whatsapp_cognitive_context_shadow(propagated, flags)

    report = {
        "program": "P19P47",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "CANARY_VALIDATION",
        "shadow_only": True,
        "runtime_mutation": False,
        "response_mutation": False,
        "feature_flags_disabled_by_default": True,
        "cognitive_context_present": "cognitive_context" in propagated,
        "safe_recovery_shadow_present": "p19p40_cognitive_context_shadow_telemetry" in propagated,
        "pipeline_shadow_present": "p19p41_cognitive_pipeline_shadow" in propagated,
        "whatsapp_shadow_present": "p19p42_whatsapp_cognitive_context_shadow" in propagated,
        "pipeline_enabled": propagated["p19p41_cognitive_pipeline_shadow"]["enabled"],
        "whatsapp_enabled": propagated["p19p42_whatsapp_cognitive_context_shadow"]["enabled"],
        "outbound_text_mutation": propagated["p19p42_whatsapp_cognitive_context_shadow"]["outbound_text_mutation"],
        "canary_passed": (
            "cognitive_context" in propagated
            and "p19p40_cognitive_context_shadow_telemetry" in propagated
            and "p19p41_cognitive_pipeline_shadow" in propagated
            and "p19p42_whatsapp_cognitive_context_shadow" in propagated
            and propagated["p19p41_cognitive_pipeline_shadow"]["enabled"] is False
            and propagated["p19p42_whatsapp_cognitive_context_shadow"]["enabled"] is False
            and propagated["p19p42_whatsapp_cognitive_context_shadow"]["outbound_text_mutation"] is False
        ),
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
