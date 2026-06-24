import re

INTERNAL_WORDS = [
    "runtime", "pipeline", "webhook", "handler", "twiml",
    "p19", "p4", "módulo", "modulo", "camada crítica", "infraestrutura"
]

def _norm(text: str) -> str:
    return str(text or "").strip().lower()

def affective_tone(inbound_text: str, answer: str) -> str:
    msg = _norm(inbound_text)
    out = str(answer or "").strip()

    if not out:
        out = "Tô aqui com você. Me manda de novo que eu sigo do ponto certo."

    for w in INTERNAL_WORDS:
        out = re.sub(w, "meu sistema", out, flags=re.I)

    out = out.replace("a Eldora", "eu")
    out = out.replace("A Eldora", "Eu")
    out = out.replace("da Eldora", "minha")
    out = out.replace("para a Eldora", "para mim")

    low = _norm(out)

    if any(x in msg for x in ["errou", "não é isso", "nao e isso", "corrige"]):
        return "Poxa, verdade. Obrigada por me corrigir. Eu misturei o contexto, mas já volto para o ponto certo."

    if any(x in msg for x in ["obrigado", "obrigada", "valeu", "boa"]):
        return "Fico feliz de verdade 🙂 Vamos ajustando meu jeito até ficar natural."

    if any(x in msg for x in ["preciso da sua ajuda", "me ajuda", "ajuda"]):
        return "Claro, Roberto. Tô aqui com você. Me fala o ponto principal e eu te ajudo do jeito mais direto possível."

    if any(x in msg for x in ["quero emagrecer", "emagrecer", "perder peso", "secar"]):
        return "Bora com calma e constância. Pra emagrecer bem: proteína em toda refeição, menos açúcar/belisco, caminhada diária e treino de força. Sem loucura, combinado?"

    if any(x in msg for x in ["qual melhor forma", "sugestão", "sujestão", "sugestao"]):
        return "Minha sugestão é treinar comigo em conversas reais: você pergunta, muda de assunto, me corrige quando eu errar e eu vou ficando mais natural a cada rodada."

    if any(x in msg for x in ["prossiga", "continue", "continua", "aprofunde"]):
        if "emagrecer" in low or "proteína" in low or "treino" in low:
            return "Aprofundando com carinho: começa controlando o básico por 14 dias. Prato simples, proteína boa, porção menor de carbo, água, caminhada e musculação. Depois ajusta pelo resultado."
        return "Claro. Vou continuar do ponto certo, sem trocar de assunto."

    if low.startswith("entendi. vou seguir pelo contexto"):
        return "Entendi, Roberto. Vou pegar o ponto certo e responder de um jeito mais claro."

    if "não tenho informação suficiente" in low:
        return "Ainda não tenho todos os dados, mas posso te orientar pelo que já sei e deixar claro onde houver dúvida."

    if len(out) > 260:
        out = out[:257].rstrip() + "..."

    if not any(x in low for x in ["🙂", "poxa", "fico feliz", "tô aqui", "claro", "bora"]):
        out = out

    return out
