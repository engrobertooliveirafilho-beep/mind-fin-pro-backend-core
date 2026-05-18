def naturalize_response(answer: str, intent: dict, state: dict, autonomous: dict) -> str:
    focus = state.get("dominant_project", "MIND")
    plan = autonomous.get("plan", {}).get("next_action", "seguir a próxima ação crítica")
    if intent.get("intent") in ["project_execution", "continuity_request"]:
        return f"Roberto, vou manter a continuidade do {focus}. O próximo movimento é claro: {plan}. Já preservei o arco atual, a prioridade P1 e o foco em execução sem resetar contexto."
    return answer
