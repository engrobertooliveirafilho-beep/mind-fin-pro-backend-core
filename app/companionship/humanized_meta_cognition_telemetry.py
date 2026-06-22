from __future__ import annotations

from datetime import datetime, timezone


def build_p19p50_unified_telemetry(ctx=None):
    ctx = dict(ctx or {})
    cognitive = dict(ctx.get("cognitive_context") or {})
    humanized = dict(cognitive.get("humanized_meta_cognition") or {})

    return {
        "program": "P19P50",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "SHADOW_CANARY",
        "cognitive_context_present": "cognitive_context" in ctx,
        "humanized_meta_cognition_present": bool(humanized),
        "safe_recovery_present": "p19p40_cognitive_context_shadow_telemetry" in ctx,
        "pipeline_present": "p19p41_cognitive_pipeline_shadow" in ctx,
        "whatsapp_present": "p19p42_whatsapp_cognitive_context_shadow" in ctx,
        "runtime_mutation": False,
        "response_mutation": False,
        "outbound_text_mutation": False,
        "production_enabled": False,
        "production_promotion": "GATED_ONLY",
        "rollbackable": True,
    }
