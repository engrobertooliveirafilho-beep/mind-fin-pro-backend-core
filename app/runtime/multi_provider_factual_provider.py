from app.runtime.ai_provider_registry import provider_registry_status, configured_text_providers
from app.runtime.real_factual_provider import real_factual_provider as openai_provider

def multi_provider_factual_provider(message: str, sender_id: str="default", context: dict|None=None) -> dict:
    providers = configured_text_providers()
    if not providers:
        return {
            "ok": False,
            "provider": "none",
            "answer": "MULTI_AI_PROVIDER_NOT_CONFIGURED",
            "registry": provider_registry_status(),
        }

    errors = []
    for p in providers:
        if p["name"] == "openai":
            r = openai_provider(message, sender_id, context)
            if r.get("ok"):
                r["fallback_used"] = "openai"
                return r
            errors.append({"provider":"openai","error":r.get("answer")})
            continue

        errors.append({"provider":p["name"],"error":"adapter_not_implemented_yet"})

    return {
        "ok": False,
        "provider": "multi_ai_failed",
        "answer": "MULTI_AI_PROVIDER_FAILED",
        "errors": errors[:10],
        "registry": provider_registry_status(),
    }
