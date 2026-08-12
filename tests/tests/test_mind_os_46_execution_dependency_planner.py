from app.runtime.execution_graph.execution_dependency_planner import plan_dependencies

def test_mind_os_46_dependency_planner_shadow_only():
    plan = plan_dependencies("como automatizar confinamento de boi")

    assert plan["mode"] == "SHADOW_ONLY"
    assert plan["shadow_only"] is True
    assert plan["execution_allowed"] is False
    assert plan["production_allowed"] is False
    assert plan["final_authority_required"] is True
    assert plan["scheduler_ready"] is True
    assert plan["cycle_detected"] is False

def test_mind_os_46_dependency_levels_cover_all_nodes():
    plan = plan_dependencies("validar runtime trader FTMO paper only")

    total_nodes_in_levels = sum(len(x["node_ids"]) for x in plan["execution_levels"])
    assert total_nodes_in_levels == plan["node_count"]
    assert plan["execution_levels_count"] >= 5

def test_mind_os_46_final_authority_last_level():
    plan = plan_dependencies("crie estratégia de marketing para eldora")

    last = plan["execution_levels"][-1]["nodes"][0]
    assert last["node_type"] == "FINAL_AUTHORITY"
    assert last["label"] == "final_authority_required"

def test_mind_os_46_all_levels_are_shadow_only():
    plan = plan_dependencies("prossiga")

    for level in plan["execution_levels"]:
        for node in level["nodes"]:
            assert node["mode"] == "SHADOW_ONLY"
            assert node["execution_allowed"] is False
            assert node["production_allowed"] is False
