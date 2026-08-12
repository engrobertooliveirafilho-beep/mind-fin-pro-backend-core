import json
from datetime import datetime, timezone

from app.companionship.cognitive_context_builder import build_cognitive_context, attach_p19p50_humanized_meta_cognition_to_context
from app.companionship.humanized_meta_cognition import build_p19p49_humanized_meta_cognition_stack
from app.companionship.safe_recovery_adapter import attach_p19p40_cognitive_context_shadow
from app.runtime.cognitive_pipeline import attach_p19p41_cognitive_context_shadow
from app.api.whatsapp import attach_p19p42_whatsapp_cognitive_context_shadow

flags = {
    "P19P50_HUMANIZED_META_COGNITION_ENABLED": False,
    "P19P50_PRODUCTION_ENABLED": False,
    "P19P41_COGNITIVE_CONTEXT_ENABLED": False,
    "P19P42_WHATSAPP_COGNITIVE_CONTEXT_ENABLED": False,
}

ctx = build_cognitive_context(user_id="p19p50c")
humanized = build_p19p49_humanized_meta_cognition_stack(
    interactions=["prossiga"],
    confirmations=["ok"],
    message_count=100,
)

ctx = attach_p19p50_humanized_meta_cognition_to_context(ctx, humanized, flags)
ctx = attach_p19p40_cognitive_context_shadow(ctx, user_id="p19p50c", feature_flags=flags)
ctx = attach_p19p41_cognitive_context_shadow(ctx, flags)
ctx = attach_p19p42_whatsapp_cognitive_context_shadow(ctx, flags)

report = {
    "program": "P19P50C",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "humanized_meta_cognition_present": "humanized_meta_cognition" in ctx.get("cognitive_context", {}),
    "p19p50_telemetry_present": "p19p50_telemetry" in ctx.get("cognitive_context", {}),
    "safe_recovery_present": "p19p40_cognitive_context_shadow_telemetry" in ctx,
    "pipeline_present": "p19p41_cognitive_pipeline_shadow" in ctx,
    "whatsapp_present": "p19p42_whatsapp_cognitive_context_shadow" in ctx,
    "pipeline_enabled": ctx["p19p41_cognitive_pipeline_shadow"]["enabled"],
    "whatsapp_enabled": ctx["p19p42_whatsapp_cognitive_context_shadow"]["enabled"],
    "outbound_text_mutation": ctx["p19p42_whatsapp_cognitive_context_shadow"]["outbound_text_mutation"],
}
report["canary_passed"] = (
    report["humanized_meta_cognition_present"]
    and report["p19p50_telemetry_present"]
    and report["safe_recovery_present"]
    and report["pipeline_present"]
    and report["whatsapp_present"]
    and report["pipeline_enabled"] is False
    and report["whatsapp_enabled"] is False
    and report["outbound_text_mutation"] is False
)
print(json.dumps(report, indent=2, ensure_ascii=False))
