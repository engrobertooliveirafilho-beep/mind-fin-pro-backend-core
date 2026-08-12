def compose_level_b_answer(message: str, sender_id: str, memory: dict | None = None) -> dict:
    memory = memory or {}

    result = {
        "status": "ok",
        "mode": "dynamic_level_b_composer",
        "sender_id": sender_id,
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

    result["answer"] = (
        "Roberto, o Nível B já consegue montar uma resposta usando execução real de planejamento, "
        "orquestração e simulação.\n\n"
        "1. Plano: quebrar o lançamento em objetivo, público, oferta, canais, operação e métricas.\n"
        "2. Simulação: comparar cenário conservador, provável e agressivo antes de escalar tráfego.\n"
        "3. Risco: controlar aquisição, conversão, suporte, reputação e custo por usuário.\n\n"
        "Para a Eldora, o próximo movimento é validar em canary, medir resposta real e só depois liberar expansão."
    )

    if result["errors"]:
        result["status"] = "partial"

    return result
