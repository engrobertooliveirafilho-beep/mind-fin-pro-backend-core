from __future__ import annotations
import re

IDENTITY_QUESTION=re.compile(r"(quem\s+(é|e)\s+(você|voce)|quem\s+eh\s+vc|qual\s+(é|e)\s+seu\s+nome)",re.I)

BANNED=[
"eu sou a eldora",
"camada conversacional do mind",
"minha função é",
"minha funcao e",
"lembrar o que importa",
"sem você precisar reexplicar",
"sem voce precisar reexplicar"
]

def contains_identity_fallback(answer:str)->bool:
    low=(answer or "").lower()
    return any(x in low for x in BANNED)

def semantic_recovery(user_message:str)->str:
    u=(user_message or "").lower()
    if "diesel" in u:
        return "Depende do que você quer comparar — diesel vs gasolina? Resumindo: diesel costuma ter mais torque e consumo menor."
    if "carro" in u:
        return "Quer visão geral sobre carro ou alguma parte específica? Motor, suspensão, manutenção, consumo?"
    if "sentiu diferença" in u or "sentiu diferenca" in u:
        return "Sim. Melhorou, mas ainda tinha um fallback antigo escapando."
    if "implanta" in u or "implata" in u:
        return "Boa. Isso ajuda bastante. Qual camada você vai mexer agora?"
    if any(x in u for x in ["que ta fazendo","oq ta fazendo","o que ta fazendo","o que você está fazendo","o que vc ta fazendo","fazendo agora"]):
        return "Estou ajustando a conversa para responder direto e manter contexto sem cair em resposta genérica."

    if "porque" in u or "pq" in u:
        return "Porque a conversa precisa manter causa e contexto, não voltar para apresentação fixa."
    if "oi" in u or "boa tarde" in u:
        return "Oi, Roberto. Estou aqui."
    return "Entendi. Continua."

def universal_recovery_answer(user_message:str, answer:str|None=None, error:Exception|None=None)->str:
    if IDENTITY_QUESTION.search(user_message or ""):
        return answer or "Sou a Eldora."
    if error is not None and not answer:
        return semantic_recovery(user_message)
    if not answer:
        return semantic_recovery(user_message)
    if contains_identity_fallback(answer):
        return semantic_recovery(user_message)
    return answer

def enforce_no_identity_in_normal_chat(user_message:str,answer:str)->str:
    return universal_recovery_answer(user_message, answer)


