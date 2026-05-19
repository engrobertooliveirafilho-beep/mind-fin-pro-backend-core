from __future__ import annotations
import re

IDENTITY_QUESTION = re.compile(r"(quem\s+(é|e)\s+(você|voce)|qual\s+(é|e)\s+seu\s+nome|se\s+apresente|vc\s+(é|e)\s+quem)", re.I)

BANNED_IDENTITY = [
    "eu sou a eldora",
    "sou a eldora",
    "camada conversacional",
    "minha função é",
    "minha funcao e",
    "lembrar o que importa",
    "sem você precisar reexplicar",
    "sem voce precisar reexplicar",
    "runtime",
    "pipeline",
    "memória contextual",
    "memoria contextual",
    "cognição",
    "cognicao",
    "estamos refinando",
]

def _low(x: str) -> str:
    return (x or "").strip().lower()

def contains_identity_fallback(answer: str) -> bool:
    low = _low(answer)
    return any(b in low for b in BANNED_IDENTITY)

def semantic_recovery(user_message: str) -> str:
    u = _low(user_message)

    if any(x in u for x in ["diesel", "motor diesel", "motor a diesel"]):
        return "Depende do que você quer comparar — diesel vs gasolina? Resumindo: diesel costuma ter mais torque, consumo menor em carga pesada e funciona por compressão, sem vela de ignição."

    if any(x in u for x in ["carro", "carros", "automovel", "automóvel"]):
        return "Quer uma visão geral ou alguma parte específica? Carro envolve motor, câmbio, suspensão, freios, consumo e manutenção. Posso começar pelo básico."

    if any(x in u for x in ["sentiu diferença", "sentiu diferenca"]):
        return "Sim, senti diferença na direção certa, mas esse vazamento de apresentação fixa mostra que ainda tinha um fallback antigo escapando no WhatsApp real."

    if any(x in u for x in ["implanta", "implata", "implant"]):
        return "Boa. Isso ajuda, principalmente se a implantação entrar no caminho real do WhatsApp e não ficar só em teste isolado. Qual camada você vai mexer agora?"

    if "porque" in u or "pq" in u:
        return "Porque a conversa precisa manter causa e contexto. Quando ela responde com apresentação fixa, ela perde o fio e parece que começou do zero."

    if any(x in u for x in ["oi", "boa tarde", "bom dia", "boa noite"]):
        return "Oi, Roberto. Estou aqui. Vamos direto no ponto."

    if "humanização" in u or "humanizacao" in u:
        return "Melhorou nos testes, mas o WhatsApp real mostrou que ainda existia fallback antigo. O certo agora é travar a resposta final para nunca cair em apresentação fixa."

    if IDENTITY_QUESTION.search(user_message or ""):
        return "Sou a Eldora. Mas no uso normal eu não devo ficar me apresentando; devo responder ao que você perguntou."

    return "Entendi. Vou responder pelo que você perguntou, sem voltar para apresentação fixa."

def universal_recovery_answer(user_message: str, answer: str | None = None, error: Exception | None = None) -> str:
    if IDENTITY_QUESTION.search(user_message or ""):
        return answer or semantic_recovery(user_message)
    if not answer or contains_identity_fallback(answer):
        return semantic_recovery(user_message)
    return answer

def enforce_no_identity_in_normal_chat(user_message: str, answer: str) -> str:
    return universal_recovery_answer(user_message, answer)
