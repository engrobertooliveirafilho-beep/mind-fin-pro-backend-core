from app.runtime.intent_arbitration_priority_engine import classify_intent

def factual_answer(text: str) -> str:
    t = (text or "").lower()

    if "qual seu nome" in t or "quem é você" in t or "quem e voce" in t:
        return "Sou seu assistente no WhatsApp."

    if "holambra" in t:
        return "Em Holambra, visite o Moinho Povos Unidos. É um dos pontos mais conhecidos e rende bom passeio no fim de semana."

    if "k1300" in t or ("bmw" in t and ("moto" in t or "pontos fortes" in t or "comprar" in t)):
        return "A BMW K1300 tem motor forte, estabilidade e conforto. Antes de comprar, cheque suspensão, elétrica, histórico e custo de manutenção."

    if "viagem" in t or "viajar" in t:
        return "Boa. Para fim de semana, escolha destino perto, revise tempo de estrada, hospedagem e um ponto principal para visitar."

    c = classify_intent(text)
    if c["intent"] in ("FACTUAL_QUESTION", "BUYING_ADVICE"):
        return "Vou direto ao ponto: preciso responder com fato útil, contexto curto e próximo passo prático."

    return ""


def factual_search_handoff(reply, message):
    ans = factual_answer(message)
    if ans:
        return ans
    return reply
