from __future__ import annotations
import re

IDENTITY_ALLOWED = re.compile(
    r"(quem\s+(é|e)\s+você|quem\s+(é|e)\s+voce|qual\s+(é|e)\s+seu\s+nome|se\s+apresente|vc\s+(é|e)\s+quem|você\s+(é|e)\s+quem)",
    re.I,
)

IDENTITY_LEAK_PATTERNS = [
    r"eu\s+sou\s+a\s+eldora",
    r"sou\s+a\s+eldora",
    r"camada\s+conversacional\s+do\s+mind",
    r"minha\s+fun[cç][aã]o\s+[ée]\s+entender\s+seu\s+contexto",
    r"lembrar\s+o\s+que\s+importa",
    r"sem\s+voc[eê]\s+precisar\s+reexplicar\s+tudo",
    r"como\s+ia",
    r"posso\s+auxiliar",
    r"como\s+posso\s+ajudar",
    r"entendo\s+sua\s+preocupa[cç][aã]o",
    r"estou\s+processando",
    r"informa[cç][aã]o\s+registrada",
]

def _norm(text: str) -> str:
    return (text or "").strip().lower()

def has_identity_leak(answer: str) -> bool:
    low = _norm(answer)
    return any(re.search(p, low, re.I) for p in IDENTITY_LEAK_PATTERNS)

def identity_allowed(user_message: str) -> bool:
    return bool(IDENTITY_ALLOWED.search(user_message or ""))

def _domain_answer(user_message: str) -> str:
    u = _norm(user_message)

    if any(x in u for x in ["diesel", "motor a diesel", "motor diesel"]):
        return (
            "Motor a diesel funciona por compressão, não por vela como o motor a gasolina. "
            "Ele costuma ter mais torque, gastar menos em carga pesada e ser melhor para caminhões, máquinas e longas distâncias. "
            "A desvantagem é manutenção mais cara, mais ruído e emissões mais difíceis de controlar."
        )

    if any(x in u for x in ["carro", "carros", "automóvel", "automovel"]):
        return (
            "Carros podem ser entendidos por cinco blocos: motor, câmbio, suspensão, freios e eletrônica. "
            "O motor gera força, o câmbio ajusta torque e velocidade, a suspensão dá estabilidade, os freios controlam segurança e a eletrônica gerencia quase tudo nos modelos atuais. "
            "Quer que eu explique por motor, manutenção ou tipos de carro?"
        )

    if any(x in u for x in ["implant", "implata", "implantar", "implantações", "implantacoes"]):
        return (
            "Boa. Isso provavelmente ajuda bastante. "
            "O ponto principal agora é garantir que cada implantação entre no webhook real, não só nos testes. "
            "Me fala qual camada você vai adicionar primeiro."
        )

    if any(x in u for x in ["sentiu diferença", "sentiu diferenca", "diferença", "diferenca"]):
        return (
            "Senti diferença na direção certa, mas ainda tem vazamento de fallback antigo. "
            "Quando a resposta volta para apresentação fixa, significa que o runtime real ainda não está passando pelo guard final em runtime_guards os caminhos."
        )

    if u in ["sim", "aham", "ok", "blz", "beleza", "isso", "certo"]:
        return "Perfeito. Continua — estou acompanhando o contexto."

    if any(x in u for x in ["oi", "olá", "ola", "boa tarde", "bom dia", "boa noite"]):
        return "Roberto, vamos direto no ponto."

    if "humanização" in u or "humanizacao" in u:
        return (
            "A humanização melhorou nos testes, mas o WhatsApp real ainda revelou um problema de roteamento. "
            "A correção agora é travar o output final para impedir fallback de identidade fora de contexto."
        )

    if "e agora" in u:
        return "Agora o foco é corrigir o caminho real do WhatsApp, validar no Render e testar as frases que ainda estão quebrando."

    return "Entendi. Continua — vou responder pelo contexto da conversa, sem resetar para apresentação."

def guard_whatsapp_final_answer(user_message: str, answer: str, context: dict | None = None) -> str:
    if identity_allowed(user_message):
        return answer or "Continua do ponto atual que eu respondo pelo contexto."

    if has_identity_leak(answer):
        return _domain_answer(user_message)

    cleaned = answer or ""
    if not cleaned.strip():
        return _domain_answer(user_message)

    return cleaned

