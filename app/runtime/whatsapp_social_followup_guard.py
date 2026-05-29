from app.runtime.intent_arbitration_priority_engine import classify_intent

def social_reply(text: str) -> str:
    t = (text or "").lower()
    c = classify_intent(text)
    if c["intent"] != "SOCIAL":
        return ""
    if "bom dia" in t: return "Bom dia! Tudo certo por aí?"
    if "boa tarde" in t: return "Boa tarde! Tudo certo por aí?"
    if "boa noite" in t: return "Boa noite! Tudo certo por aí?"
    if "tudo bem" in t: return "Tudo bem por aqui. E você?"
    if "bem" in t: return "Boa. Vamos em frente."
    return "Oi! Tudo certo?"

def whatsapp_social_followup_guard(text: str):
    return social_reply(text)

def block_meta_reply(reply):
    low = str(reply or "").lower()
    return ("diagnóstico" in low and "estratégia" in low and "execução" in low) or ("não posso" in low and "política" in low)
