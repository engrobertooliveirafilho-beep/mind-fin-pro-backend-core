from datetime import datetime, timezone

def run_level_b_shadow(message: str = "", sender_id: str = "unknown", context: dict | None = None):
    context = context or {}
    lower = (message or "").lower()

    trace = {
        "status": "ok",
        "mode": "shadow_only",
        "sender_id": sender_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "capabilities": {
            "agent_orchestrator": False,
            "distributed_runtime": False,
            "swarm": False,
            "predictive_simulation": False,
            "hierarchical_plan": False,
        },
        "signals": [],
        "recommendation": None,
    }

    if any(x in lower for x in ["plano", "estratégia", "estrategia", "passo", "lançar", "lancar", "simular", "prever"]):
        trace["capabilities"]["agent_orchestrator"] = True
        trace["capabilities"]["hierarchical_plan"] = True
        trace["signals"].append("planning_context")

    if any(x in lower for x in ["swarm", "multi", "agente", "agentes", "distribuído", "distribuido"]):
        trace["capabilities"]["distributed_runtime"] = True
        trace["capabilities"]["swarm"] = True
        trace["signals"].append("multi_agent_context")

    if any(x in lower for x in ["simular", "prever", "cenário", "cenario", "risco", "impacto"]):
        trace["capabilities"]["predictive_simulation"] = True
        trace["signals"].append("simulation_context")

    if trace["signals"]:
        trace["recommendation"] = (
            "Level B detectou contexto de planejamento/simulação/orquestração. "
            "A resposta final pode se beneficiar de decomposição, simulação e análise multiagente."
        )

    return trace
