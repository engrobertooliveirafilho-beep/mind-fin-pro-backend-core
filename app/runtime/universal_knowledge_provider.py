from __future__ import annotations

def _norm(text: str) -> str:
    return str(text or "").strip().lower()

def detect_universal_domain(text: str, previous_domain: str = "") -> str:
    t = _norm(text)

    rules = {
        "fitness": ["emagrecer", "dieta", "proteína", "proteina", "suplemento", "fisiculturista", "treino", "cardio", "massa", "gordura"],
        "sports": ["jogo", "brasil", "futebol", "seleção", "selecao", "placar", "escalação", "escalacao"],
        "tech": ["render", "github", "runtime", "deploy", "webhook", "api", "python", "erro", "teste", "sistema"],
        "marketing": ["copy", "criativo", "anúncio", "anuncio", "campanha", "funil", "lead", "venda", "instagram", "tiktok"],
        "trader": ["trade", "trader", "ftmo", "backtest", "drawdown", "winrate", "paper", "estratégia", "estrategia"],
        "automotive": ["carro", "mercedes", "classe a", "marcha", "embreagem", "atuador", "câmbio", "cambio"],
        "relationship": ["triste", "feliz", "ansioso", "cansado", "frustrado", "preciso de ajuda", "me ajuda"],
    }

    for domain, words in rules.items():
        if any(w in t for w in words):
            return domain

    if any(x in t for x in ["prossiga", "continue", "continua", "aprofunde", "quanto", "quais", "como faço", "como faco", "monta", "monte"]):
        return previous_domain or "general"

    return previous_domain or "general"

def detect_universal_intent(text: str) -> str:
    t = _norm(text)

    if any(x in t for x in ["errou", "não entendi", "nao entendi", "frase pronta", "repete", "não é isso", "nao e isso"]):
        return "correction"
    if any(x in t for x in ["monte", "monta", "crie", "faça", "faca", "organize"]):
        return "create"
    if any(x in t for x in ["quais informações", "o que precisa", "que dados", "quais dados"]):
        return "slot_request"
    if any(x in t for x in ["quais", "quanto", "qual", "como", "por que", "quando"]):
        return "question"
    if any(x in t for x in ["prossiga", "continue", "continua", "aprofunde", "detalhe"]):
        return "followup"
    if any(x in t for x in ["oi", "olá", "ola", "tudo bem"]):
        return "social"

    return "general"

def universal_provider_answer(domain: str, intent: str, text: str, state: dict) -> str:
    t = _norm(text)

    if intent == "correction":
        return "Poxa, você tem razão. Eu não vou repetir frase pronta. Vou voltar para o ponto certo e responder pelo que você pediu."

    if domain == "fitness":
        if "fisiculturista" in t:
            return "Para uma dieta estilo fisiculturista, eu preciso calcular macros. Me passe peso, altura, idade, horário do treino e objetivo: secar, ganhar massa ou recompor."
        if "suplement" in t:
            return "Os básicos são: creatina 3–5 g/dia, whey se faltar proteína e cafeína se você tolerar. Mas suplemento só ajusta o plano; dieta e treino mandam mais."
        if "quais informações" in t or "o que precisa" in t:
            return "Preciso de peso, altura, idade, horário do treino, quantas refeições faz, alimentos que gosta, alimentos que evita e se tem lesão ou restrição."
        if "prote" in t or "quanto" in t:
            return "Para emagrecer preservando massa, use 1,6 a 2,2 g de proteína por kg. Se estiver perto de 93 kg, mira entre 150 e 200 g por dia."
        if "monte" in t or "monta" in t or "dieta" in t:
            return "Monto sim. Base inicial: café com ovos ou whey; almoço com proteína, arroz, feijão e salada; lanche com iogurte/whey/fruta; jantar com proteína e legumes. Para fechar quantidades, preciso dos seus dados."
        if "rápido" in t or "rapido" in t:
            return "O jeito mais rápido sem fazer loucura é déficit calórico, proteína alta, treino de força e caminhada diária. Cortar açúcar, bebida calórica e belisco já acelera muito."
        return "Vamos fazer direito: primeiro eu preciso dos seus dados para montar um plano real, não genérico."

    if domain == "sports":
        return "Sobre jogo atual, eu preciso de busca real para confirmar adversário, escalação e momento. Sem isso, eu só consigo te dar uma análise geral."

    if domain == "marketing":
        return "No marketing, eu começaria por promessa, público, dor, oferta e criativo. Depois testaria 3 ângulos: direto, história curta e prova."

    if domain == "trader":
        return "No trader, primeiro valida hipótese em paper: ativo, timeframe, entrada, stop, alvo, drawdown e amostra. Sem isso, não promove nada."

    if domain == "tech":
        return "Na parte técnica, eu separaria diagnóstico, causa raiz, patch mínimo, teste e evidência. Sem isso vira remendo."

    if domain == "automotive":
        return "No automotivo, o certo é isolar sintoma, testar causa provável e só depois trocar peça. Primeiro evidência, depois decisão."

    if domain == "relationship":
        return "Tô aqui com você. Me fala o que pegou primeiro, e eu te ajudo com calma."

    if intent == "followup":
        last = state.get("last_answer", "")
        return f"Continuando do ponto anterior: {last[:180]}"

    return "Me dá só o objetivo principal: você quer plano, diagnóstico, explicação ou próximo passo?"

# ============================================================
# P2404 GOAL MANAGER RESPONSE
# ============================================================

def goal_manager_response(domain: str, intent: str, text: str, state: dict) -> str | None:
    t = _norm(text)

    if domain == "fitness":
        state["goal"] = state.get("goal") or "montar dieta personalizada"

        if any(x in t for x in ["dieta especifica", "dieta específica", "minha dieta", "montar dieta", "monte minha dieta"]):
            state["goal"] = "coletar dados para dieta personalizada"
            return (
                "Perfeito. Pra eu montar uma dieta específica pra você, preciso destes dados: "
                "peso, altura, idade, horário do treino, quantas refeições faz por dia, alimentos que gosta, "
                "alimentos que evita e objetivo principal: secar, ganhar massa ou recompor."
            )

        if any(x in t for x in ["aprofunde", "prossiga", "continue", "detalhe"]):
            if "dieta" in str(state.get("goal","")):
                return (
                    "Aprofundando: primeiro eu coleto seus dados, depois calculo proteína, distribuo refeições, "
                    "ajusto carbo perto do treino e deixo opções simples para repetir sem sofrer."
                )

    return None
