from app.runtime.intent_arbitration_priority_engine import classify_intent
from app.runtime.factual_search_handoff import factual_answer
from app.runtime.whatsapp_social_followup_guard import social_reply

def _calc_text(text: str) -> str:
    import re
    raw = (text or "").lower().replace(",", ".")
    expr = raw.replace("quanto é", "").replace("quanto e", "").replace("calcule", "")
    expr = re.sub(r"[^0-9+\-*/(). ]", "", expr)
    if any(op in expr for op in ["+","-","*","/"]) and any(ch.isdigit() for ch in expr):
        if re.fullmatch(r"[0-9+\-*/(). ]+", expr):
            try:
                return str(eval(expr, {"__builtins__": {}}, {}))
            except Exception:
                return ""
    return ""

def route_natural_whatsapp(text: str) -> str:
    calc = _calc_text(text)
    if calc:
        return calc

    c = classify_intent(text)
    intent = c["intent"]

    if intent in ("FACTUAL_QUESTION", "BUYING_ADVICE"):
        ans = factual_answer(text)
        if ans:
            return ans[:220]

    if intent == "SOCIAL":
        ans = factual_answer(text) or social_reply(text)
        if ans:
            return ans[:220]

    if intent == "FOLLOWUP":
        return "Aprofundando: o próximo passo é separar causa, impacto e ação prática."

    if intent == "TASK_VERIFICATION":
        return "Vou verificar por evidência: critério, teste, log e conclusão."

    if intent == "OPEN_LOOP":
        return "Me diga o tema em uma frase para eu seguir direto."

    return "Não entendi com precisão. Reformule em uma frase mais clara."
