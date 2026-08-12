from app.runtime.execution_graph.dependency_inference_engine import infer_dependency_dag

def test_mind_os_46a_shadow_only():
    dag = infer_dependency_dag("como automatizar confinamento de boi")

    assert dag["mode"] == "SHADOW_ONLY"
    assert dag["shadow_only"] is True
    assert dag["execution_allowed"] is False
    assert dag["production_allowed"] is False
    assert dag["final_authority_required"] is True
    assert dag["cycle_detected"] is False
    assert dag["scheduler_ready"] is True

def test_mind_os_46a_parallelism_exists_for_system_design():
    dag = infer_dependency_dag("como automatizar confinamento de boi")

    assert dag["parallelizable_levels_count"] >= 1

def test_mind_os_46a_quality_guard_after_terminal_caps():
    dag = infer_dependency_dag("prossiga")

    qg = [n for n in dag["nodes"] if n["node_type"] == "QUALITY_GUARD"][0]
    incoming = [e for e in dag["edges"] if e["to"] == qg["node_id"]]

    assert len(incoming) >= 1
    assert all(e["production_allowed"] is False for e in incoming)

def test_mind_os_46a_final_authority_terminal():
    dag = infer_dependency_dag("validar runtime trader FTMO paper only")

    final = dag["nodes"][-1]
    assert final["node_type"] == "FINAL_AUTHORITY"

    outgoing = [e for e in dag["edges"] if e["from"] == final["node_id"]]
    assert outgoing == []

def test_mind_os_46a_capability_nodes_have_uid():
    dag = infer_dependency_dag("crie estratégia de marketing para eldora")

    caps = [n for n in dag["nodes"] if n["node_type"] == "CAPABILITY"]
    assert len(caps) >= 3

    for c in caps:
        assert c["uid"].startswith("CAP_")
        assert c["mode"] == "SHADOW_ONLY"
        assert c["execution_allowed"] is False
        assert c["production_allowed"] is False
