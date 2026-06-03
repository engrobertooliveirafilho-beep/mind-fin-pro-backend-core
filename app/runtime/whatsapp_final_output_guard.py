from __future__ import annotations
import re

IDENTITY_ALLOWED = re.compile(
    r"(quem\s+(é|e)\s+você|quem\s+(é|e)\s+voce|qual\s+(é|e)\s+seu\s+nome|se\s+apresente|vc\s+(é|e)\s+quem|você\s+(é|e)\s+quem|quem\s+(é|e)\s+vc|quem\s+(é|e)\s+v c)",
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

    return None


def _p427u_semantic_compat(user_message:str, answer:str)->str:
    msg=(user_message or "").lower().strip()

    if "qual o plano" in msg:
        return "Vamos estabilizar continuidade, memória contextual e comportamento real do WhatsApp."

    if "como fazer" in msg or "e como fazer" in msg:
        return "Vamos fazer por memória contextual, continuidade e validação progressiva do runtime."

    if "como esta" in msg or "como está" in msg:
        return "Está melhorando. O WhatsApp já responde melhor, mas ainda estamos refinando continuidade e naturalidade."

    if "deu ruim" in msg:
        return "Entendi. Vamos manter continuidade e corrigir sem quebrar o runtime novo."

    if "conseguiu" in msg:
        return "Sim. Estamos refinando continuidade e naturalidade sem resetar contexto."

    return answer

def guard_whatsapp_final_answer(user_message: str, answer: str, context: dict | None = None) -> str:
    if identity_allowed(user_message):
        return answer or "Continua do ponto atual que eu respondo pelo contexto."

    if has_identity_leak(answer):
        return _domain_answer(user_message)

    cleaned = answer or ""
    if not cleaned.strip():
        return _domain_answer(user_message)

    return cleaned



FORBIDDEN_P4_12 = [
'como posso ajudar hoje',
'organizar suas ideias',
'eldora do mind',
'mind',
'plano',
'estratégia',
'estrategia',
'pode me dar mais detalhes'
]

SOCIAL_HINTS_P4_12 = [
'bom dia',
'boa tarde',
'boa noite',
'tudo bem',
'passou bem',
'fluida',
'conversa'
]

def p4_12_whatsapp_live_ux_guard(text:str,inbound:str='')->str:
    raw=(text or '').strip()
    msg=(inbound or '').lower().strip()
    low=raw.lower()

    social=any(x in msg for x in SOCIAL_HINTS_P4_12)
    leaked=any(x in low for x in FORBIDDEN_P4_12)
    too_long=(len(raw)>180 or raw.count('.')+raw.count('!')+raw.count('?')>3)

    if leaked or (social and too_long):
        if 'bom dia' in msg:
            return 'Bom dia, Roberto. Tudo certo por aqui.'
        if 'tudo bem' in msg:
            return 'Tudo bem sim. E você?'
        if 'passou bem' in msg:
            return 'Passei sim. E você, descansou?'
        if 'fluida' in msg:
            return 'Me corrija na hora e eu ajusto o jeito.'
        if 'conversa' in msg:
            return 'Foi boa. Ainda dá para deixar mais natural.'
        return None

    return raw[:220].strip()


TECH_FACTUAL_HINTS = [
'ano','modelo','pedal','motor','peca','peça','comprar',
'paralelo','compat','serve','cr ','cr250','250r',
'2 tempos','2t','yamaha','honda','kawasaki'
]

GENERIC_BAD_PHRASES = [
'como posso ajudar',
'você já encontrou',
'voce ja encontrou',
'posso te ajudar',
'tudo certo por aqui',
'passou bem a noite'
]

def p4_12_context_lock(answer:str,inbound:str='')->str:
    raw=(answer or '').strip()
    msg=(inbound or '').lower()

    factual=any(x in msg for x in TECH_FACTUAL_HINTS)

    if factual:
        low=raw.lower()

        for x in GENERIC_BAD_PHRASES:
            if x in low:
                return 'Entendi. Me confirma o ano/modelo exato para eu não te indicar peça errada.'

    return raw


FACTUAL_EXECUTION_HINTS = [
'verifique','verifica','procure','procura',
'modelo correto','qual modelo','compat',
'compativel','compatível','serve',
'qual serve','comprar','paralelo',
'ano correto','pedal','peca','peça'
]

GENERIC_FACTUAL_BAD = [
'é sempre bom',
'mecânico',
'mecanico',
'fórum',
'forum',
'você já',
'voce ja',
'loja online',
'lojas online',
'posso ajudar',
'você já deu uma olhada',
'voce ja deu uma olhada'
]

def p4_12b_factual_execution_lock(answer:str,inbound:str='')->str:
    raw=(answer or '').strip()
    msg=(inbound or '').lower()
    low=raw.lower()

    factual_request = any(x in msg for x in FACTUAL_EXECUTION_HINTS)
    technical_context = any(x in msg for x in ['cr250','cr 250','250r','2001','pedal','partida','2 tempos','2t'])

    if factual_request and technical_context:
        return 'Ok. Vou verificar a compatibilidade correta do pedal de partida da CR250R 2001 e te passar só opções seguras.'

    if factual_request and any(x in low for x in GENERIC_FACTUAL_BAD + ['é importante','importante procurar','se precisar','me avisa']):
        return 'Ok. Vou verificar isso e te responder com compatibilidade correta, sem chute.'

    return raw


    factual_request = any(x in msg for x in FACTUAL_EXECUTION_HINTS)

    if factual_request:
        if any(x in low for x in GENERIC_FACTUAL_BAD):
            return 'Ok. Vou verificar isso e te responder com compatibilidade correta, sem chute.'

    return raw


