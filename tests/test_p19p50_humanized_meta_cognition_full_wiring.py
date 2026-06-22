from app.companionship.cognitive_context_builder import (
    build_cognitive_context,
    attach_p19p50_humanized_meta_cognition_to_context,
)
from app.companionship.humanized_meta_cognition import (
    build_p19p49_humanized_meta_cognition_stack,
)
from app.companionship.humanized_meta_cognition_telemetry import (
    build_p19p50_unified_telemetry,
)
from app.companionship.safe_recovery_adapter import attach_p19p40_cognitive_context_shadow
from app.runtime.cognitive_pipeline import attach_p19p41_cognitive_context_shadow
from app.api.whatsapp import attach_p19p42_whatsapp_cognitive_context_shadow


def test_p19p50_attaches_humanized_stack_to_cognitive_context():
    base = build_cognitive_context(user_id="u1")
    humanized = build_p19p49_humanized_meta_cognition_stack(
        interactions=["a"],
        confirmations=["b"],
        current_preferences={"style": "direct"},
    )

    result = attach_p19p50_humanized_meta_cognition_to_context(
        base,
        humanized,
        {
            "P19P50_HUMANIZED_META_COGNITION_ENABLED": False,
            "P19P50_PRODUCTION_ENABLED": False,
        },
    )

    cc = result["cognitive_context"]

    assert "humanized_meta_cognition" in cc
    assert cc["p19p50_telemetry"]["enabled"] is False
    assert cc["p19p50_telemetry"]["production_enabled"] is False
    assert cc["p19p50_telemetry"]["runtime_mutation"] is False
    assert cc["p19p50_telemetry"]["response_mutation"] is False


def test_p19p50_end_to_end_shadow_pipeline():
    flags = {
        "P19P50_HUMANIZED_META_COGNITION_ENABLED": False,
        "P19P50_PRODUCTION_ENABLED": False,
        "P19P41_COGNITIVE_CONTEXT_ENABLED": False,
        "P19P42_WHATSAPP_COGNITIVE_CONTEXT_ENABLED": False,
    }

    ctx = build_cognitive_context(user_id="u2")
    humanized = build_p19p49_humanized_meta_cognition_stack(
        interactions=["prossiga"],
        confirmations=["ok"],
    )

    ctx = attach_p19p50_humanized_meta_cognition_to_context(ctx, humanized, flags)
    ctx = attach_p19p40_cognitive_context_shadow(ctx, user_id="u2")
    ctx = attach_p19p41_cognitive_context_shadow(ctx, flags)
    ctx = attach_p19p42_whatsapp_cognitive_context_shadow(ctx, flags)

    assert "humanized_meta_cognition" in ctx["cognitive_context"]
    assert "p19p40_cognitive_context_shadow_telemetry" in ctx
    assert "p19p41_cognitive_pipeline_shadow" in ctx
    assert "p19p42_whatsapp_cognitive_context_shadow" in ctx
    assert ctx["p19p41_cognitive_pipeline_shadow"]["enabled"] is False
    assert ctx["p19p42_whatsapp_cognitive_context_shadow"]["enabled"] is False
    assert ctx["p19p42_whatsapp_cognitive_context_shadow"]["outbound_text_mutation"] is False


def test_p19p50_unified_telemetry_contract():
    ctx = {
        "cognitive_context": {
            "humanized_meta_cognition": {"program": "P19P49"}
        },
        "p19p40_cognitive_context_shadow_telemetry": {},
        "p19p41_cognitive_pipeline_shadow": {},
        "p19p42_whatsapp_cognitive_context_shadow": {},
    }

    telemetry = build_p19p50_unified_telemetry(ctx)

    assert telemetry["program"] == "P19P50"
    assert telemetry["humanized_meta_cognition_present"] is True
    assert telemetry["safe_recovery_present"] is True
    assert telemetry["pipeline_present"] is True
    assert telemetry["whatsapp_present"] is True
    assert telemetry["production_enabled"] is False
    assert telemetry["production_promotion"] == "GATED_ONLY"
