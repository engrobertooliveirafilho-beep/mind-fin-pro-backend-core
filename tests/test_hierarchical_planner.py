from app.planning.hierarchical_planner import (
    HierarchicalPlanner,
    HierarchicalPlan,
    SubTaskPlan,
)
import pytest


def test_build_plan_creates_multi_level_structure():
    planner = HierarchicalPlanner()
    plan = planner.build_plan(
        goal="Executar MIND fase 2 com horizonte longo",
        horizon_steps=9,
        memory_summary=None,
    )
    assert isinstance(plan, HierarchicalPlan)
    levels = {s.level for s in plan.steps}
    assert 0 in levels and 1 in levels and 2 in levels
    assert plan.root_goal.startswith("Executar MIND")


def test_next_actions_respect_parent_dependencies():
    planner = HierarchicalPlanner()
    # plano manual para controlar o grafo
    root = SubTaskPlan(id="root", level=0, description="root")
    mid = SubTaskPlan(id="mid-1", level=1, description="mid", parent_id="root")
    leaf = SubTaskPlan(id="mid-1-leaf-1", level=2, description="leaf", parent_id="mid-1")
    plan = HierarchicalPlan(root_goal="g", steps=[root, mid, leaf])

    # nada concluído -> primeiro mid (pai) antes do leaf
    actions = planner.next_actions(plan, completed_ids=[])
    ids = [a.id for a in actions]
    assert "mid-1" in ids
    # conclui mid -> agora leaf vira executável
    actions2 = planner.next_actions(plan, completed_ids=["mid-1"])
    ids2 = [a.id for a in actions2]
    assert "mid-1-leaf-1" in ids2


def test_memory_summary_influences_leaf_descriptions():
    planner = HierarchicalPlanner()
    summary = "cliente VIP XPTO com histórico longo de interação"
    plan = planner.build_plan(
        goal="Montar plano de longo prazo",
        horizon_steps=6,
        memory_summary=summary,
    )
    leaf_texts = [s.description for s in plan.steps if s.level == 2]
    assert any("XPTO" in t or "cliente VIP" in t for t in leaf_texts)



@pytest.mark.parametrize("horizon", [1, 2, 5, 7, 13])
def test_exact_horizon(horizon):
    assert len(HierarchicalPlanner().build_plan("goal", horizon).leaves()) == horizon

def test_atomic_dependency_rejection():
    planner = HierarchicalPlanner()
    plan = planner.build_plan("goal", 6)
    with pytest.raises(ValueError):
        planner.next_actions(plan, ["mid-1", "mid-2-leaf-1"])
    assert not any(s.done for s in plan.steps)

@pytest.mark.parametrize("cid", ["root", "unknown"])
def test_invalid_completion(cid):
    planner = HierarchicalPlanner()
    plan = planner.build_plan("goal", 6)
    with pytest.raises(ValueError):
        planner.next_actions(plan, [cid])
    assert not any(s.done for s in plan.steps)
