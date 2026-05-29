from app.runtime.intent_arbitration_priority_engine import classify_intent
from app.runtime.factual_search_handoff import factual_answer
from app.runtime.whatsapp_social_followup_guard import social_reply
from app.runtime.ux_scoreboard import score_message

def route_natural_whatsapp(text: str) -> str:
    c = classify_intent(text)
    intent = c["intent"]

    if intent == "CALCULATION":
        try:
            safe = "".join(ch for ch in text.replace(",", ".") if ch in "0123456789+-*/(). ")
            return str(eval(safe, {"__builtins__": {}}, {}))
        except Exception:
            return "Não consegui calcular com segurança."

    if intent in ("FACTUAL_QUESTION", "BUYING_ADVICE"):
        ans = factual_answer(text)
        if ans:
            return ans[:220]

    if intent == "SOCIAL":
        ans = social_reply(text)
        if ans:
            return ans[:220]

    if intent == "FOLLOWUP":
        return "Aprofundando: o próximo passo é separar causa, impacto e ação prática."

    if intent == "TASK_VERIFICATION":
        return "Vou verificar por evidência: critério, teste, log e conclusão."

    if intent == "OPEN_LOOP":
        return "Me diga o tema em uma frase para eu seguir direto."

    return "Não entendi com precisão. Reformule em uma frase mais clara."
