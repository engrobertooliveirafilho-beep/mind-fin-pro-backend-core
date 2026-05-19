from __future__ import annotations

def is_state_query(text: str) -> bool:
    t=(text or "").lower()
    return any(x in t for x in [
        "estado atual",
        "resuma o estado",
        "onde estamos",
        "status atual",
        "snapshot",
        "baseline"
    ])

def build_mind_state_visible_response() -> str:
    return (
        "Resumo técnico do MIND/Eldora:\n"
        "- Runtime estável V2 ativo.\n"
        "- Testes verdes: 194/194.\n"
        "- Render operacional.\n"
        "- Twilio/WhatsApp validado com entrega real.\n"
        "- Webhook produtivo respondendo.\n"
        "- Camada de inteligência WhatsApp acoplada.\n"
        "- Gap atual: resposta visível ainda precisa usar memória/contexto MIND completo.\n"
        "Próximo passo: conectar resposta visível ao estado real, memória persistente e orquestração."
    )

