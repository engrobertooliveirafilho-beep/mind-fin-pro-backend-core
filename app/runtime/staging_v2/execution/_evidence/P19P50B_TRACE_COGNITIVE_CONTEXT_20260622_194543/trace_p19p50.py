import json

from app.companionship.cognitive_context_builder import (
    build_cognitive_context,
    attach_p19p50_humanized_meta_cognition_to_context,
)

from app.companionship.humanized_meta_cognition import (
    build_p19p49_humanized_meta_cognition_stack,
)

from app.companionship.safe_recovery_adapter import (
    attach_p19p40_cognitive_context_shadow,
)

from app.runtime.cognitive_pipeline import (
    attach_p19p41_cognitive_context_shadow,
)

from app.api.whatsapp import (
    attach_p19p42_whatsapp_cognitive_context_shadow,
)

flags = {
    "P19P50_HUMANIZED_META_COGNITION_ENABLED": False,
    "P19P50_PRODUCTION_ENABLED": False,
    "P19P41_COGNITIVE_CONTEXT_ENABLED": False,
    "P19P42_WHATSAPP_COGNITIVE_CONTEXT_ENABLED": False,
}

ctx = build_cognitive_context(user_id="trace")

print("\nSTEP_1_BUILD")
print(json.dumps(
    list(ctx.get("cognitive_context", {}).keys()),
    indent=2
))

humanized = build_p19p49_humanized_meta_cognition_stack(
    interactions=["prossiga"],
    confirmations=["ok"]
)

ctx = attach_p19p50_humanized_meta_cognition_to_context(
    ctx,
    humanized,
    flags,
)

print("\nSTEP_2_AFTER_P19P50")
print("humanized_meta_cognition" in ctx.get("cognitive_context", {}))
print(json.dumps(
    list(ctx.get("cognitive_context", {}).keys()),
    indent=2
))

ctx = attach_p19p40_cognitive_context_shadow(
    ctx,
    user_id="trace"
)

print("\nSTEP_3_AFTER_P19P40")
print("humanized_meta_cognition" in ctx.get("cognitive_context", {}))
print(json.dumps(
    list(ctx.get("cognitive_context", {}).keys()),
    indent=2
))

ctx = attach_p19p41_cognitive_context_shadow(
    ctx,
    flags,
)

print("\nSTEP_4_AFTER_P19P41")
print("humanized_meta_cognition" in ctx.get("cognitive_context", {}))
print(json.dumps(
    list(ctx.get("cognitive_context", {}).keys()),
    indent=2
))

ctx = attach_p19p42_whatsapp_cognitive_context_shadow(
    ctx,
    flags,
)

print("\nSTEP_5_AFTER_P19P42")
print("humanized_meta_cognition" in ctx.get("cognitive_context", {}))
print(json.dumps(
    list(ctx.get("cognitive_context", {}).keys()),
    indent=2
))
