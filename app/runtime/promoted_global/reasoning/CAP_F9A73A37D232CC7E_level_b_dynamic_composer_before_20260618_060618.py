def _detect_domain(message: str) -> str:
    text = (message or "").lower()

    if any(x in text for x in ["eldora", "lançar", "lancar", "lançamento", "lancamento", "instagram", "tiktok", "whatsapp", "marketing"]):
        return "digital_launch"

    if any(x in text for x in ["trader", "trade", "ftmo", "backtest", "paper", "mercado"]):
        return "mind_trader"

    if any(x in text for x in ["treino", "academia", "dieta", "emagrecer", "musculação", "musculacao"]):
        return "fitness"

    if any(x in text for x in ["estudar", "estudo", "prova", "concurso", "faculdade"]):
        return "study"

    return "general_strategy"


def _build_enriched_answer(message: str, components: dict, domain: str) -> str:
    planner = components.get("plan", {}) or {}
    simulation = components.get("simulation", {}) or {}
    orchestration = components.get("orchestration", {}) or {}

    root_goal = planner.get("root_goal") or message
    tasks_created = orchestration.get("tasks_created", 0)
    confidence = (
        simulation.get("prediction", {}).get("confidence")
        if isinstance(simulation.get("prediction"), dict)
        else None
    )

    if domain == "digital_launch":
        return (
            f"Roberto, para esse objetivo — {root_goal} — eu montaria a execução em 5 blocos.\n\n"
            "1. Objetivo: validar a Eldora como produto conversacional no WhatsApp antes de escalar tráfego.\n"
            "2. Oferta: deixar claro o que ela resolve primeiro: estudo, treino, organização, rotina e suporte rápido.\n"
            "3. Aquisição: usar Instagram, TikTok, YouTube Shorts e status do WhatsApp com CTA direto para conversa.\n"
            "4. Simulação: trabalhar três cenários: conservador com baixa conversão, provável com tração gradual e agressivo com viralização.\n"
            "5. Risco: controlar promessa exagerada, custo de aquisição, volume de suporte, resposta genérica e quebra de continuidade.\n\n"
            f"Sinal do orquestrador: {tasks_created} tarefas detectadas.\n"
            f"Confiança da simulação: {confidence if confidence is not None else 'não informada'}.\n\n"
            "Próxima ação: rodar um canary com 10 a 30 conversas reais controladas, medir retenção, perguntas repetidas, objeções e intenção de pagamento. "
            "Só depois disso vale ampliar tráfego."
        )

    if domain == "mind_trader":
        return (
            f"Roberto, para esse objetivo — {root_goal} — a resposta correta é separar pesquisa, simulação e risco operacional.\n\n"
            "1. Pesquisa: validar hipóteses apenas em dados históricos e paper.\n"
            "2. Simulação: comparar drawdown, payoff, winrate, robustez e degradação.\n"
            "3. Risco: manter LIVE/REAL bloqueado até certificação externa e regras da conta parametrizadas.\n"
            "4. Execução: nada de ordem real sem aprovação explícita.\n\n"
            f"Sinal do orquestrador: {tasks_created} tarefas detectadas.\n"
            f"Confiança da simulação: {confidence if confidence is not None else 'não informada'}.\n\n"
            "Próxima ação: expandir backtests, validar walk-forward e só depois discutir ambiente FTMO controlado."
        )

    return (
        f"Roberto, para esse objetivo — {root_goal} — eu estruturaria em plano, simulação e risco.\n\n"
        "1. Plano: quebrar o objetivo em fases executáveis.\n"
        "2. Simulação: testar cenário conservador, provável e agressivo.\n"
        "3. Risco: mapear gargalos, dependências e pontos de falha.\n"
        "4. Métrica: definir como saber se funcionou.\n\n"
        f"Sinal do orquestrador: {tasks_created} tarefas detectadas.\n"
        f"Confiança da simulação: {confidence if confidence is not None else 'não informada'}.\n\n"
        "Próxima ação: executar primeiro em modo controlado, medir resposta real e só depois escalar."
    )


def compose_level_b_answer(message: str, sender_id: str, memory: dict | None = None) -> dict:
    memory = memory or {}

    result = {
        "status": "ok",
        "mode": "dynamic_level_b_composer_enriched",
        "sender_id": sender_id,
        "domain": _detect_domain(message),
        "answer": None,
        "components": {},
        "errors": []
    }

    context = {
        "sender_id": sender_id,
        "memory": memory,
        "production_enabled": False,
        "real_user_sent": False
    }

    try:
        from app.eldora.core.agent_orchestrator import orchestrate
        result["components"]["orchestration"] = orchestrate(goal=message, context=context)
    except Exception as exc:
        result["errors"].append({"component": "orchestration", "error": str(exc)})

    try:
        from app.eldora.core.predictive_simulation_engine import run_simulation
        result["components"]["simulation"] = run_simulation(goal=message, context=context)
    except Exception as exc:
        result["errors"].append({"component": "simulation", "error": str(exc)})

    try:
        from app.p7_adapters.hierarchical_planner_adapter import plan
        result["components"]["plan"] = plan(goal=message, context=context)
    except Exception as exc:
        result["errors"].append({"component": "plan", "error": str(exc)})

    result["answer"] = _build_enriched_answer(
        message=message,
        components=result["components"],
        domain=result["domain"]
    )

    if result["errors"]:
        result["status"] = "partial"

    return result
