from app.p7_adapters.hierarchical_contracts import (
    HierarchicalPlanRequest,
    HierarchicalPlanResponse,
    HierarchyNode,
)
from app.p7_adapters.hierarchical_planner_adapter import plan_hierarchy
from app.p7_adapters.oversight_contracts import OversightInput, OversightDecision
from app.p7_adapters.oversight_shadow_adapter import review_or_guard


def test_hierarchical_contracts_validate():
    req = HierarchicalPlanRequest(
        user_intent="criar plano",
        goal="organizar execução",
    )
    assert req.goal == "organizar execução"
    assert req.max_depth == 3


def test_plan_hierarchy_returns_serializable_response():
    req = HierarchicalPlanRequest(
        user_intent="criar empresa e lançar Eldora",
        goal="lançar Eldora",
    )
    res = plan_hierarchy(req)

    assert isinstance(res, HierarchicalPlanResponse)
    assert res.root_goal == "lançar Eldora"
    assert res.execution_order == ["root"]
    assert res.next_action == "shadow_plan_ready"
    assert res.model_dump()


def test_hierarchy_node_schema():
    node = HierarchyNode(
        node_id="n1",
        title="fase 1",
        objective="preparar base",
    )
    assert node.status == "planned"
    assert node.children == []


def test_oversight_contracts_validate():
    payload = OversightInput(
        candidate_action="executar build",
        reasoning_summary="há risco sem testes",
    )
    assert payload.execution_mode == "shadow"


def test_review_or_guard_allow_without_risk():
    payload = OversightInput(
        candidate_action="planejar sem alterar código",
        reasoning_summary="ação segura",
    )
    decision = review_or_guard(payload)

    assert isinstance(decision, OversightDecision)
    assert decision.decision == "ALLOW"
    assert decision.allowed is True
    assert decision.risk_level == "LOW"
    assert "no_runtime_mutation" in decision.audit_trace


def test_review_or_guard_review_with_risk():
    payload = OversightInput(
        candidate_action="executar build",
        reasoning_summary="risco detectado",
        risk_flags=["no_tests"],
    )
    decision = review_or_guard(payload)

    assert decision.decision == "REVIEW"
    assert decision.allowed is True
    assert decision.risk_level == "MEDIUM"
    assert "no_blocking_enforcement" in decision.audit_trace
