from app.p7_adapters.hierarchical_contracts import (
    HierarchicalPlanRequest,
    HierarchicalPlanResponse,
    HierarchyNode,
)

def plan_hierarchy(req: HierarchicalPlanRequest) -> HierarchicalPlanResponse:
    root = HierarchyNode(
        node_id="root",
        title=req.goal,
        objective=req.user_intent,
        status="planned",
        children=[],
    )

    return HierarchicalPlanResponse(
        root_goal=req.goal,
        nodes=[root],
        execution_order=["root"],
        next_action="shadow_plan_ready",
        audit_trace=["p7_adapter", "no_runtime_mutation"],
    )

def plan(goal=None, context=None):
    req = HierarchicalPlanRequest(goal=goal, user_intent=goal, context=context or {})
    response = plan_hierarchy(req)
    data = response if isinstance(response, dict) else response.__dict__.copy()
    return _p450b_enrich_plan(data, goal or "")
def _p450b_detect_domain(goal: str) -> str:
    text = (goal or "").lower()
    if any(x in text for x in ["eldora", "lançar", "lancar", "lançamento", "lancamento", "marketing", "instagram", "tiktok", "whatsapp"]):
        return "digital_launch"
    if any(x in text for x in ["trader", "trade", "ftmo", "backtest", "paper", "mercado"]):
        return "mind_trader"
    return "general_strategy"


def _p450b_node(node_id, parent_id, title, objective, dependencies=None, suggested_tool=None):
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


def _p450b_enrich_plan(data: dict, goal: str) -> dict:
    domain = _p450b_detect_domain(goal)

    if domain == "digital_launch":
        nodes = [
            _p450b_node("root", None, goal, goal),
            _p450b_node("phase_1_positioning", "root", "Definir posicionamento", "Clarificar promessa, público inicial e caso de uso principal.", [], "marketing_strategy"),
            _p450b_node("phase_2_offer", "root", "Construir oferta inicial", "Transformar a Eldora em uma oferta simples de entrada pelo WhatsApp.", ["phase_1_positioning"], "offer_design"),
            _p450b_node("phase_3_content", "root", "Gerar aquisição orgânica", "Publicar conteúdo curto com CTA direto para conversa.", ["phase_2_offer"], "content_engine"),
            _p450b_node("phase_4_canary", "root", "Rodar canary controlado", "Validar 10 a 30 conversas reais na allowlist antes de escalar.", ["phase_3_content"], "canary_runtime"),
            _p450b_node("phase_5_metrics", "root", "Medir conversão e retenção", "Acompanhar ativação, retenção, intenção de pagamento e objeções.", ["phase_4_canary"], "analytics")
        ]
        data["risk_flags"] = ["promessa_exagerada", "resposta_generica", "baixa_retencao", "alto_custo_aquisicao", "quebra_continuidade"]
        data["tool_requirements"] = ["marketing_strategy", "offer_design", "content_engine", "canary_runtime", "analytics"]
        data["next_action"] = "execute_controlled_canary"

    elif domain == "mind_trader":
        nodes = [
            _p450b_node("root", None, goal, goal),
            _p450b_node("phase_1_research", "root", "Validar hipótese", "Separar hipótese de trading de execução real.", [], "research_engine"),
            _p450b_node("phase_2_backtest", "root", "Rodar backtest", "Medir payoff, drawdown, winrate e robustez.", ["phase_1_research"], "backtest_engine"),
            _p450b_node("phase_3_stress", "root", "Rodar stress test", "Testar degradação, slippage e cenários ruins.", ["phase_2_backtest"], "stress_engine"),
            _p450b_node("phase_4_paper", "root", "Validar em paper", "Executar sem ordem real até certificação.", ["phase_3_stress"], "paper_runtime")
        ]
        data["risk_flags"] = ["overfitting", "drawdown_alto", "violacao_regras_ftmo", "ordem_real_nao_autorizada"]
        data["tool_requirements"] = ["research_engine", "backtest_engine", "stress_engine", "paper_runtime"]
        data["next_action"] = "execute_paper_validation"

    else:
        nodes = [
            _p450b_node("root", None, goal, goal),
            _p450b_node("phase_1_scope", "root", "Definir escopo", "Clarificar objetivo, restrições e resultado esperado.", [], "planning"),
            _p450b_node("phase_2_execution", "root", "Executar piloto", "Testar em ambiente controlado.", ["phase_1_scope"], "execution"),
            _p450b_node("phase_3_measurement", "root", "Medir resultado", "Avaliar evidência antes de escalar.", ["phase_2_execution"], "analytics")
        ]
        data["risk_flags"] = ["escopo_vago", "metricas_fracas", "execucao_sem_evidencia"]
        data["tool_requirements"] = ["planning", "execution", "analytics"]
        data["next_action"] = "execute_controlled_validation"

    for n in nodes:
        n["children"] = [x["node_id"] for x in nodes if x.get("parent_id") == n["node_id"]]

    data["domain"] = domain
    data["nodes"] = nodes
    data["execution_order"] = [n["node_id"] for n in nodes]
    return data


