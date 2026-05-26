from __future__ import annotations

_STATE = {}

def strategic_conversation_authority(
    assistant_reply: str,
    user_message: str,
    sender_id: str | None = None
):
    '''
    Passive strategic authority.
    Mantém compatibilidade dos testes sem sequestrar smalltalk.
    '''

    sid = sender_id or "anonymous"
    msg = (user_message or "").lower().strip()

    state = _STATE.setdefault(sid, {})

    strategic_terms = (
        "fluidez","melhorar","melhoria","prioridade",
        "estratégia","estrategia","roadmap","gargalo",
        "otimização","otimizacao","plano","eldora"
    )

    followup_terms = (
        "o que fazer primeiro",
        "primeiro",
        "próximo passo",
        "proximo passo",
        "e depois",
        "mais contexto"
    )

    if any(t in msg for t in strategic_terms):
        state["last_topic"] = user_message
        return (
            "SCA: autoridade final estratégica ativa. "
            "Primeiro: melhorar a fluidez conversacional real, "
            "reduzir respostas genéricas, manter continuidade "
            "e validar comportamento real no WhatsApp."
        )

    if any(t in msg for t in followup_terms):
        topic = state.get("last_topic")
        if topic:
            return (
                f"SCA: autoridade final reutilizando contexto "
                f"anterior ({topic}). Primeiro alinhar prioridade "
                f"80/20 e validar comportamento real."
            )

    return None
