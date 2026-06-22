from app.companionship.cognitive_context_builder import (
    build_cognitive_context,
    attach_p19p50_humanized_meta_cognition_to_context,
)
from app.companionship.humanized_meta_cognition import (
    build_p19p49_humanized_meta_cognition_stack,
)
from app.companionship.safe_recovery_adapter import attach_p19p40_cognitive_context_shadow
from app.runtime.cognitive_pipeline import attach_p19p41_cognitive_context_shadow
from app.api.whatsapp import attach_p19p42_whatsapp_cognitive_context_shadow


def test_p19p50c_safe_recovery_preserves_humanized_meta_cognition():
    flags = {
        "P19P50_HUMANIZED_META_COGNITION_ENABLED": False,
        "P19P50_PRODUCTION_ENABLED": False,
        "P19P41_COGNITIVE_CONTEXT_ENABLED": False,
        "P19P42_WHATSAPP_COGNITIVE_CONTEXT_ENABLED": False,
    }

    ctx = build_cognitive_context(user_id="u")
    humanized = build_p19p49_humanized_meta_cognition_stack(
        interactions=["prossiga"],
        confirmations=["ok"],
    )

    ctx = attach_p19p50_humanized_meta_cognition_to_context(ctx, humanized, flags)
    assert "humanized_meta_cognition" in ctx["cognitive_context"]

    ctx = attach_p19p40_cognitive_context_shadow(ctx, user_id="u", feature_flags=flags)
    assert "humanized_meta_cognition" in ctx["cognitive_context"]
    assert "p19p50_telemetry" in ctx["cognitive_context"]
    assert "humanized_meta_cognition" in ctx["p19p40_cognitive_context_shadow_telemetry"]["preserved_cognitive_context_keys"]

    ctx = attach_p19p41_cognitive_context_shadow(ctx, flags)
    ctx = attach_p19p42_whatsapp_cognitive_context_shadow(ctx, flags)

    assert "humanized_meta_cognition" in ctx["cognitive_context"]
    assert ctx["p19p41_cognitive_pipeline_shadow"]["enabled"] is False
    assert ctx["p19p42_whatsapp_cognitive_context_shadow"]["enabled"] is False
    assert ctx["p19p42_whatsapp_cognitive_context_shadow"]["outbound_text_mutation"] is False
