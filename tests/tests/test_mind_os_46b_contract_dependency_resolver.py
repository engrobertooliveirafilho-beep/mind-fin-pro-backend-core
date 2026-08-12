from app.runtime.execution_graph.contract_dependency_resolver import resolve_contract_dependencies

def test_mind_os_46b_shadow_only():
    plan = resolve_contract_dependencies("como automatizar confinamento de boi")

    assert plan["mode"] == "SHADOW_ONLY"
    assert plan["shadow_only"] is True
    assert plan["execution_allowed"] is False
    assert plan["production_allowed"] is False
    assert plan["cycle_detected"] is False
    assert plan["scheduler_ready"] is True

def test_mind_os_46b_capabilities_have_contract_fields():
    plan = resolve_contract_dependencies("crie estratégia de marketing para eldora")
    caps = [n for n in plan["nodes"] if n["node_type"] == "CAPABILITY"]

    assert len(caps) >= 3
    for c in caps:
        assert c["uid"].startswith("CAP_")
        assert isinstance(c["requires"], list)
        assert isinstance(c["provides"], list)
        assert c["production_allowed"] is False

def test_mind_os_46b_edges_have_dependency_reason():
    plan = resolve_contract_dependencies("validar runtime trader FTMO paper only")

    dependency_edges = [e for e in plan["edges"] if "dependency_reason" in e]
    assert len(dependency_edges) >= 1

def test_mind_os_46b_final_authority_terminal():
    plan = resolve_contract_dependencies("prossiga")

    final = plan["nodes"][-1]
    assert final["node_type"] == "FINAL_AUTHORITY"

    outgoing = [e for e in plan["edges"] if e["from"] == final["node_id"]]
    assert outgoing == []

def test_mind_os_46b_quality_guard_exists():
    plan = resolve_contract_dependencies("como automatizar confinamento de boi")
    qg = [n for n in plan["nodes"] if n["node_type"] == "QUALITY_GUARD"]
    assert len(qg) == 1
