from typing import Dict, Any

def classify_intent(message: str) -> Dict[str, Any]:
    text = (message or "").strip().lower()

    if text in {"oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"}:
        return {"intent": "GREETING", "needs_short_reply": True}

    if text in {"tudo bem?", "tudo bem", "td bem?", "td bem"}:
        return {"intent": "CHECKIN", "needs_short_reply": True}

    if "implementações novas" in text or "implementacoes novas" in text:
        if "quais" in text or "quais são" in text or "quais sao" in text or "aspectos" in text:
            return {"intent": "IMPLEMENTATION_ASPECTS", "needs_short_reply": True}
        return {"intent": "IMPLEMENTATION_OPINION", "needs_short_reply": True}

    if text in {"prossiga", "continua", "continue"}:
        return {"intent": "CONTINUE_CONTEXT", "needs_short_reply": True}

    if any(x in text for x in ["tenho um problema", "me ajuda", "preciso de ajuda"]):
        return {"intent": "ASK_PROBLEM", "needs_short_reply": True}

    if "procure" in text and "envie" in text:
        return {"intent": "FETCH_PREVIOUS_REQUEST", "needs_short_reply": True}

    if "link" in text and ("youtube" in text or "música" in text or "musica" in text):
        return {"intent": "FETCH_LINK", "needs_short_reply": True}

    if any(x in text for x in ["quais são", "quais sao", "cite", "liste"]):
        return {"intent": "DIRECT_LIST", "needs_short_reply": True}

    return {"intent": "DIRECT_ANSWER", "needs_short_reply": True}
