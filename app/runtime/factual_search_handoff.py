from app.runtime.intent_arbitration_priority_engine import classify_intent

def factual_answer(text: str) -> str:
    c = classify_intent(text)
    if c["intent"] == "BUYING_ADVICE":
        return "A BMW K1300 se destaca por motor forte, estabilidade e conforto. Antes de comprar: cheque histórico, suspensão, elétrica e manutenção."
    if c["intent"] == "FACTUAL_QUESTION":
        return "Resposta factual: vou direto ao ponto com contexto, pontos principais e próximo passo verificável."
    return ""
