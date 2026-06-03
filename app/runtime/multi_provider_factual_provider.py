from app.runtime.ai_provider_registry import provider_registry_status, configured_text_providers
from app.runtime.text_provider_adapters import call_provider

def multi_provider_factual_provider(message: str, sender_id: str="default", context: dict|None=None) -> dict:
    providers = configured_text_providers()
    if not providers:
        return {"ok":False,"provider":"none","answer":"MULTI_AI_PROVIDER_NOT_CONFIGURED","registry":provider_registry_status()}

    errors=[]
    for p in providers:
        try:
            answer = call_provider(p["name"], message, p.get("model"), context)
            if answer and answer.strip():
                return {"ok":True,"provider":p["name"],"model":p.get("model"),"answer":answer[:900],"errors":errors}
            errors.append({"provider":p["name"],"error":"empty_answer"})
        except Exception as e:
            errors.append({"provider":p["name"],"error":repr(e)[:500]})

    return {"ok":False,"provider":"multi_ai_failed","answer":"MULTI_AI_PROVIDER_FAILED","errors":errors,"registry":provider_registry_status()}
