def naturalize_response(answer: str, intent: dict, state: dict, autonomous: dict) -> str:
    name = "Roberto"
    focus = state.get("dominant_project", "MIND")
    raw_intent = intent.get("intent", "casual_context")
    text_hint = (state.get("last_unresolved_topic") or "").lower()
    plan = autonomous.get("plan", {}).get("next_action", "avançar a próxima camada crítica")

    if text_hint.strip() in ["ok", "certo", "beleza", "show"]:
        return f"Fechado. Vou manter o foco no {focus} e avançar sem reiniciar o contexto."

    if "achou" in text_hint or "opinião" in text_hint:
        return f"Eu achei um avanço real, {name}. A Eldora saiu do modo resposta mecânica e entrou num fluxo com continuidade. Ainda falta naturalidade: ela entende o arco, mas às vezes fala como relatório. O próximo ajuste é deixar a resposta mais humana sem perder estratégia."

    if raw_intent in ["project_execution", "continuity_request", "casual_context"]:
        return f"{name}, sigo no fio do {focus}. O próximo movimento é {plan}. A parte boa: já temos continuidade, memória e execução. A parte que ainda precisa lapidar é a conversa soar menos engessada."

    if raw_intent == "emotional_presence":
        return f"Entendi, {name}. Vou manter presença e direção: sem dramatizar, sem desviar. Primeiro estabilizo o contexto; depois avanço a ação mais útil."

    return answer if "Diagnóstico:" not in answer else f"{name}, entendi o ponto. Vou responder direto e manter o contexto do {focus}: {plan}."
