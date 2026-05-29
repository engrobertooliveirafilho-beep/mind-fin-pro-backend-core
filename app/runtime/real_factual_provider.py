import json, os, urllib.request

OPENAI_URL = "https://api.openai.com/v1/responses"

def real_factual_provider(message: str, sender_id: str="default", context: dict|None=None) -> dict:
    key = os.getenv("OPENAI_API_KEY","").strip()
    if not key:
        return {"ok": False, "provider": "none", "answer": "FACTUAL_PROVIDER_NOT_CONFIGURED"}

    prompt = (
        "Responda em português do Brasil, estilo WhatsApp, direto, útil e factual. "
        "Não invente ranking nem dados atuais. Se precisar de dado atualizado, diga isso objetivamente. "
        f"Contexto: {json.dumps(context or {}, ensure_ascii=False)}\n"
        f"Mensagem: {message}"
    )

    payload = {
        "model": os.getenv("OPENAI_MODEL","gpt-4.1-mini"),
        "input": prompt,
        "temperature": 0.2,
        "max_output_tokens": 300
    }

    try:
        req = urllib.request.Request(
            OPENAI_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.loads(r.read().decode("utf-8"))

        text = data.get("output_text")
        if not text:
            parts = []
            for item in data.get("output", []):
                for content in item.get("content", []):
                    if content.get("text"):
                        parts.append(content["text"])
            text = "\n".join(parts).strip()

        return {"ok": bool(text), "provider": "openai_responses", "answer": (text or "FACTUAL_PROVIDER_EMPTY")[:900]}

    except Exception as e:
        detail = type(e).__name__
        try:
            detail += ":" + str(getattr(e, "code", ""))
            body = e.read().decode("utf-8", errors="ignore")[:500] if hasattr(e, "read") else ""
            if body:
                detail += ":" + body
        except Exception:
            pass
        return {"ok": False, "provider": "openai_error", "answer": "FACTUAL_PROVIDER_ERROR: " + detail}
