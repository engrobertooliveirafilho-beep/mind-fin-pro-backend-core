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


def _fmt_scenarios(simulation: dict) -> str:
    scenarios = simulation.get("scenarios", []) or []
    if not scenarios:
        return "- cenários ainda não detalhados"

    lines = []
    for s in scenarios[:3]:
        lines.append(
            f"- {s.get('name','cenário')}: probabilidade {s.get('probability','?')} | impacto {s.get('impact','?')} | {s.get('description','')}"
        )
    return "\n".join(lines)


def _fmt_plan(planner: dict) -> str:
    nodes = planner.get("nodes", []) or []
    phases = [n for n in nodes if n.get("node_id") != "root"]

    if not phases:
        return "- Definir escopo\n- Executar piloto\n- Medir resultado"

    lines = []
    for n in phases[:6]:
        deps = n.get("dependencies") or []
        dep_txt = f" depende de {', '.join(deps)}" if deps else " sem dependência inicial"
        lines.append(f"- {n.get('title')}: {n.get('objective')}{dep_txt}.")
    return "\n".join(lines)


def _fmt_risks(planner: dict, simulation: dict) -> str:
    risks = []
    risks.extend(planner.get("risk_flags", []) or [])
    risks.extend(simulation.get("risk_flags", []) or [])

    unique = []
    for r in risks:
        if r not in unique:
            unique.append(r)

    if not unique:
        return "- risco ainda não classificado"

    return "\n".join([f"- {r}" for r in unique[:8]])


def _domain_profile(domain: str) -> dict:
    profiles = {
        "digital_launch": {
            "header": "Roberto, para lançar a Eldora, isso deve ser tratado como validação de produto + aquisição + retenção, não só como campanha.",
            "metrics": ["conversas iniciadas", "retenção 24h/7d", "perguntas repetidas", "intenção de pagamento", "custo por conversa qualificada"],
            "guardrail": "Não escalar tráfego antes de validar retenção e promessa."
        },
        "mind_trader": {
            "header": "Roberto, para MIND Trader, a regra é separar pesquisa, paper e risco. Nada de operação real sem certificação explícita.",
            "metrics": ["profit factor", "drawdown", "walk-forward", "stress test", "consistência em paper"],
            "guardrail": "LIVE/REAL/FTMO_REAL permanecem bloqueados."
        },
        "fitness": {
            "header": "Roberto, para treino/fitness, a prioridade é resultado sustentável sem quebrar articulação nem recuperação.",
            "metrics": ["frequência semanal", "dor articular", "progressão de carga", "medidas", "energia/recuperação"],
            "guardrail": "Sem progressão agressiva se houver dor persistente."
        },
        "study": {
            "header": "Roberto, para estudo, o objetivo é transformar esforço em retenção e acerto, não só aumentar horas.",
            "metrics": ["horas líquidas", "acertos por tema", "erros recorrentes", "revisões concluídas", "nota em simulado"],
            "guardrail": "Sem avançar conteúdo antes de corrigir erros recorrentes."
        },
        "general_strategy": {
            "header": "Roberto, eu estruturaria isso como plano controlado com simulação e medição antes de escalar.",
            "metrics": ["execução", "retenção", "custo", "qualidade", "risco"],
            "guardrail": "Sem escalar antes de evidência mínima."
        }
    }
    return profiles.get(domain, profiles["general_strategy"])


def _build_enriched_answer(message: str, components: dict, domain: str) -> str:
    planner = components.get("plan", {}) or {}
    simulation = components.get("simulation", {}) or {}
    orchestration = components.get("orchestration", {}) or {}

    profile = _domain_profile(domain)

    root_goal = planner.get("root_goal") or message
    tasks_created = orchestration.get("tasks_created", 0)
    confidence = simulation.get("prediction", {}).get("confidence") if isinstance(simulation.get("prediction"), dict) else None

    plan_txt = _fmt_plan(planner)
    scenario_txt = _fmt_scenarios(simulation)
    risk_txt = _fmt_risks(planner, simulation)
    metrics_txt = "\n".join([f"- {m}" for m in profile["metrics"]])
    recommendation = simulation.get("recommendation") or planner.get("next_action") or "executar validação controlada"

    return (
        f"{profile['header']}\n\n"
        f"Objetivo: {root_goal}\n\n"
        "Plano operacional:\n"
        f"{plan_txt}\n\n"
        "Simulação de cenários:\n"
        f"{scenario_txt}\n\n"
        "Riscos principais:\n"
        f"{risk_txt}\n\n"
        "Métricas que devem mandar na decisão:\n"
        f"{metrics_txt}\n\n"
        f"Sinal do orquestrador: {tasks_created} tarefas detectadas.\n"
        f"Confiança da simulação: {confidence if confidence is not None else 'não informada'}.\n\n"
        f"Guardrail: {profile['guardrail']}\n"
        f"Próxima ação: {recommendation}"
    )


def compose_level_b_answer(message: str, sender_id: str, memory: dict | None = None) -> dict:
    memory = memory or {}

    result = {
        "status": "ok",
        "mode": "dynamic_level_b_composer_domain_specialized",
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
