from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class HierarchicalPlanRequest:
    goal: str | None = None
    context: dict | None = None


@dataclass
class HierarchicalPlanResponse:
    root_goal: str
    nodes: list
    execution_order: list
    tool_requirements: list
    risk_flags: list
    next_action: str


def _detect_domain(goal: str) -> str:
    text = (goal or "").lower()

    if any(x in text for x in ["eldora", "lançar", "lancar", "lançamento", "lancamento", "marketing", "instagram", "tiktok", "whatsapp"]):
        return "digital_launch"

    if any(x in text for x in ["trader", "trade", "ftmo", "backtest", "paper", "mercado"]):
        return "mind_trader"

    if any(x in text for x in ["treino", "academia", "dieta", "emagrecer", "musculação", "musculacao"]):
        return "fitness"

    if any(x in text for x in ["estudo", "estudar", "prova", "concurso", "faculdade"]):
        return "study"

    return "general_strategy"


def _node(node_id: str, parent_id: str | None, title: str, objective: str, dependencies=None, suggested_tool=None):
    return {
        "node_id": node_id,
        "parent_id": parent_id,
        "title": title,
        "objective": objective,
        "status": "planned",
        "dependencies": dependencies or [],
        "children": [],
        "suggested_tool": suggested_tool
    }


def _build_domain_nodes(goal: str, domain: str) -> tuple[list, list, list, list]:
    nodes = [
        _node("root", None, goal, goal)
    ]

    if domain == "digital_launch":
        additions = [
            _node("phase_1_positioning", "root", "Definir posicionamento", "Clarificar promessa, público inicial e caso de uso principal.", [], "marketing_strategy"),
            _node("phase_2_offer", "root", "Construir oferta inicial", "Transformar a Eldora em uma oferta simples de entrada pelo WhatsApp.", ["phase_1_positioning"], "offer_design"),
            _node("phase_3_content", "root", "Gerar aquisição orgânica", "Publicar conteúdo curto com CTA direto para conversa.", ["phase_2_offer"], "content_engine"),
            _node("phase_4_canary", "root", "Rodar canary controlado", "Validar 10 a 30 conversas reais na allowlist antes de escalar.", ["phase_3_content"], "canary_runtime"),
            _node("phase_5_metrics", "root", "Medir conversão e retenção", "Acompanhar ativação, retenção, intenção de pagamento e objeções.", ["phase_4_canary"], "analytics")
        ]
        risks = [
            "promessa_exagerada",
            "resposta_generica",
            "baixa_retencao",
            "alto_custo_aquisicao",
            "quebra_continuidade"
        ]
        tools = [
            "marketing_strategy",
            "offer_design",
            "content_engine",
            "canary_runtime",
            "analytics"
        ]

    elif domain == "mind_trader":
        additions = [
            _node("phase_1_research", "root", "Validar hipótese", "Separar hipótese de trading de execução real.", [], "research_engine"),
            _node("phase_2_backtest", "root", "Rodar backtest", "Medir payoff, drawdown, winrate e robustez.", ["phase_1_research"], "backtest_engine"),
            _node("phase_3_stress", "root", "Rodar stress test", "Testar degradação, slippage e cenários ruins.", ["phase_2_backtest"], "stress_engine"),
            _node("phase_4_paper", "root", "Validar em paper", "Executar sem ordem real até certificação.", ["phase_3_stress"], "paper_runtime")
        ]
        risks = [
            "overfitting",
            "drawdown_alto",
            "violacao_regras_ftmo",
            "ordem_real_nao_autorizada"
        ]
        tools = [
            "research_engine",
            "backtest_engine",
            "stress_engine",
            "paper_runtime"
        ]

    else:
        additions = [
            _node("phase_1_scope", "root", "Definir escopo", "Clarificar objetivo, restrições e resultado esperado.", [], "planning"),
            _node("phase_2_execution", "root", "Executar piloto", "Testar em ambiente controlado.", ["phase_1_scope"], "execution"),
            _node("phase_3_measurement", "root", "Medir resultado", "Avaliar evidência antes de escalar.", ["phase_2_execution"], "analytics")
        ]
        risks = [
            "escopo_vago",
            "metricas_fracas",
            "execucao_sem_evidencia"
        ]
        tools = [
            "planning",
            "execution",
            "analytics"
        ]

    nodes.extend(additions)

    for n in nodes:
        n["children"] = [x["node_id"] for x in nodes if x.get("parent_id") == n["node_id"]]

    execution_order = [n["node_id"] for n in nodes]
    return nodes, execution_order, tools, risks


def plan_hierarchy(req: HierarchicalPlanRequest) -> HierarchicalPlanResponse:
    goal = req.goal or "undefined_goal"
    domain = _detect_domain(goal)
    nodes, execution_order, tools, risks = _build_domain_nodes(goal, domain)

    return HierarchicalPlanResponse(
        root_goal=goal,
        nodes=nodes,
        execution_order=execution_order,
        tool_requirements=tools,
        risk_flags=risks,
        next_action="execute_controlled_canary" if domain == "digital_launch" else "execute_controlled_validation"
    )


def plan(goal=None, context=None):
    req = HierarchicalPlanRequest(goal=goal, context=context or {})
    response = plan_hierarchy(req)
    data = asdict(response)
    data["domain"] = _detect_domain(goal or "")
    return data
