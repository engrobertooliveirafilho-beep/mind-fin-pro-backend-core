import json, os, urllib.request, urllib.error

OPENAI_URL = "https://api.openai.com/v1/chat/completions"

def real_factual_provider(message: str, sender_id: str="default", context: dict|None=None) -> dict:
    key = os.getenv("OPENAI_API_KEY","").strip()
    if not key:
        return {
            "ok": False,
            "provider": "none",
            "answer": "FACTUAL_PROVIDER_NOT_CONFIGURED"
        }

    payload = {
        "model": os.getenv("OPENAI_MODEL","gpt-4o-mini"),
        "messages": [
            {
                "role":"system",
                "content":"Você responde WhatsApp em PT-BR. Direto, útil, factual, curto e sem inventar dados."
            },
            {
                "role":"user",
                "content": message
            }
        ],
        "temperature": 0.2
    }

    try:
        req = urllib.request.Request(
            OPENAI_URL,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type":"application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode())

        answer = data["choices"][0]["message"]["content"].strip()

        return {
            "ok": True,
            "provider": "openai",
            "answer": answer[:900]
        }

    except Exception as e:
        detail = type(e).__name__
        try:
            detail += ":" + str(getattr(e, "code", ""))
            body = e.read().decode("utf-8", errors="ignore")[:300] if hasattr(e, "read") else ""
            if body:
                detail += ":" + body
        except Exception:
            pass
        return {"ok": False, "provider": "openai_error", "answer": "FACTUAL_PROVIDER_ERROR: " + detail}

