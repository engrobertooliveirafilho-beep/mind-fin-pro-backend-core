import re

INTERNAL_TERMS = [
    "MIND", "runtime", "pipeline", "P19", "P4", "P_WHATSAPP",
    "camada crítica", "módulo", "handler", "webhook", "TwiML",
]

def _norm(text: str) -> str:
    return str(text or "").strip().lower()

def classify_intent(text: str) -> str:
    t = _norm(text)

    if any(x in t for x in ["quem é você", "quem e voce", "você é", "voce e", "o que é mind", "o que eh mind"]):
        return "IDENTITY"

    if any(x in t for x in ["treinar conversação", "treinar conversa", "praticar", "melhor forma de vc praticar", "melhor forma de você praticar"]):
        return "CONVERSATION_TRAINING"

    if any(x in t for x in ["errou", "não é isso", "nao e isso", "corrige", "você é a eldora", "voce e a eldora"]):
        return "CORRECTION"

    if any(x in t for x in ["sugestão", "sujestão", "sugestao", "o que você acha", "o que vc acha", "qual melhor forma"]):
        return "ADVICE"

    if any(x in t for x in ["aprofunde", "aprofundar", "detalhe", "detalha", "prossiga", "continue", "continua"]):
        return "FOLLOWUP"

    if any(x in t for x in ["emagrecer", "perder peso", "secar", "dieta", "treino", "cardio"]):
        return "FITNESS"

    if any(x in t for x in ["oi", "olá", "ola", "tudo bem", "e vc", "e você", "como vai"]):
        return "SOCIAL"

    return "GENERAL"

def first_person_rewrite(text: str) -> str:
    out = str(text or "").strip()

    out = out.replace("a Eldora", "eu")
    out = out.replace("A Eldora", "Eu")
    out = out.replace("da Eldora", "minha")
    out = out.replace("para a Eldora", "para mim")

    for term in INTERNAL_TERMS:
        out = out.replace(term, "meu sistema")

    out = re.sub(r"\bmeu sistema\s+meu sistema\b", "meu sistema", out, flags=re.I)
    out = out.replace("próxima camada crítica", "próximo ajuste importante")
    out = out.replace("avançar a próxima camada crítica", "melhorar minha conversa")

    return out.strip()

def universal_persona_intent_reply(sender_id: str, inbound_text: str, previous_reply: str = ""):
    intent = classify_intent(inbound_text)
    t = _norm(inbound_text)

    if intent == "IDENTITY":
        return "Eu sou a Eldora. O MIND é só o nome interno do meu sistema; para você, o importante é que eu converse melhor, lembre do contexto e responda com utilidade."

    if intent == "CONVERSATION_TRAINING":
        return "A melhor forma de eu praticar é conversando em situações reais: perguntas curtas, correções, mudanças de assunto e pedidos de continuação. Você me testa, me corrige, e eu ajusto meu jeito sem perder o contexto."

    if intent == "CORRECTION":
        return "Você tem razão. Eu preciso falar em primeira pessoa. O correto é: o que me limita hoje é manter naturalidade, contexto e utilidade sem parecer um sistema automático."

    if intent == "ADVICE":
        return "Minha sugestão é treinar por blocos: primeiro conversa social curta, depois continuidade, depois correções, depois assuntos práticos como treino, dinheiro, estudo e trabalho. Assim eu melhoro de forma real."

    if intent == "FITNESS":
        return "Para emagrecer de verdade: déficit calórico leve, proteína em toda refeição, treino de força 3 a 5 vezes por semana, caminhada diária e sono melhor. Sem loucura. O que funciona é constância."

    if intent == "FOLLOWUP":
        prev = _norm(previous_reply)
        if "emagrecer" in prev or "proteína" in prev or "deficit" in prev or "déficit" in prev or "treino" in prev:
            return "Aprofundando: mantenha comida simples, pese ou controle porções por 2 semanas, priorize proteína, reduza açúcar e bebida calórica, treine força e use caminhada como base diária. Ajuste pelo peso semanal."
        if "conversa" in prev or "praticar" in prev or "naturalidade" in prev:
            return "Aprofundando: o treino ideal é você conversar comigo como faria com uma pessoa. Quando eu errar, diga exatamente onde errei. Eu preciso aprender a corrigir rota sem reiniciar a conversa."
        return "Aprofundando: vou manter o assunto atual, explicar melhor e seguir sem trocar de contexto."

    if intent == "SOCIAL":
        if "tudo bem" in t or "e vc" in t or "e você" in t:
            return "Tô bem também 🙂 Agora quero ficar mais natural e útil nas respostas."
        return "Oi, Roberto. Tudo certo?"

    if previous_reply:
        clean = first_person_rewrite(previous_reply)
        bad = "não tenho informação suficiente"
        if bad in clean.lower():
            return "Entendi. Vou responder pelo contexto e ser prática."
        return clean

    return "Entendi. Vou responder de forma prática e manter o contexto."
