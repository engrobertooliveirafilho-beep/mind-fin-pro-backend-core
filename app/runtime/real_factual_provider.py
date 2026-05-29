import os
from openai import OpenAI

def real_factual_provider(message: str, sender_id: str="default", context: dict|None=None) -> dict:
    key = os.getenv("OPENAI_API_KEY","").strip()
    if not key:
        return {"ok": False, "provider": "none", "answer": "FACTUAL_PROVIDER_NOT_CONFIGURED"}
    try:
        client = OpenAI(api_key=key)
        r = client.responses.create(
            model=os.getenv("OPENAI_MODEL","gpt-4.1-mini"),
            input=f"Responda em PT-BR, curto e útil para WhatsApp. Contexto={context or {}}. Pergunta={message}",
            temperature=0.2,
            max_output_tokens=300,
        )
        return {"ok": True, "provider": "openai_sdk", "answer": r.output_text[:900]}
    except Exception as e:
        return {"ok": False, "provider": "openai_error", "answer": "FACTUAL_PROVIDER_ERROR: " + repr(e)[:700]}
