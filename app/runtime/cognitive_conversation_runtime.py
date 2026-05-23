
from dataclasses import dataclass

@dataclass(frozen=True)
class TurnDecision:
    turn_type: str
    allow_factual_memory: bool
    allow_topic_reuse: bool
    reason: str

def decide_turn(inbound: str, previous_state=None) -> TurnDecision:
    text = (inbound or "").strip().lower()
    if not text:
        return TurnDecision("EMPTY", False, False, "empty input")

    social = [
        "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "tudo bem",
        "tudo e vc", "e vc", "blz", "beleza", "que foi", "como assim"
    ]
    meta = [
        "como eu te deixo", "mais fluida", "melhorar sua resposta",
        "você está", "voce está", "seu comportamento", "sua conversa"
    ]
    recovery = [
        "não entendi", "nao entendi", "deu errado", "erro", "não era isso",
        "nao era isso", "explica melhor"
    ]

    explicit_factual = [
        "verifique", "verificar", "verifi", "pesquise", "pesquisar", "procure", "procurar", "calcule", "calcular", "compare", "comparar", "valide", "validar", "confirme", "confirmar", "analise", "analisar",
        "qual", "quanto", "onde", "quando", "preço", "valor", "link",
        "modelo", "ano", "compatível", "compativel", "serve", "documento",
        "arquivo", "contrato", "nota", "relatório", "relatorio"
    ]

    if any(x in text for x in meta):
        return TurnDecision("META_CONVERSATION", False, False, "meta conversation blocks factual carryover")

    if any(x in text for x in social):
        return TurnDecision("SOCIAL_DIALOGUE", False, False, "social dialogue blocks factual carryover")

    if any(x in text for x in recovery):
        return TurnDecision("RECOVERY", False, False, "recovery blocks stale factual state")

    if any(x in text for x in explicit_factual):
        return TurnDecision("FACTUAL_TASK", True, True, "explicit factual signal in current turn")

    if previous_state and getattr(previous_state, "active_subject", "") and len(text.split()) <= 8:
        return TurnDecision("OPEN_FOLLOWUP", False, False, "open followup cannot inherit factual state without explicit signal")

    return TurnDecision("GENERAL_DIALOGUE", False, False, "default safe dialogue")
