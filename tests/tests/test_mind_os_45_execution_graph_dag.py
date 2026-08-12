from app.runtime.execution_graph.execution_graph_dag import build_execution_dag

def test_mind_os_45_dag_shadow_only():
    dag = build_execution_dag("como automatizar confinamento de boi")

    assert dag["mode"] == "SHADOW_ONLY"
    assert dag["shadow_only"] is True
    assert dag["execution_allowed"] is False
    assert dag["production_allowed"] is False
    assert dag["final_authority_required"] is True
    assert dag["is_dag"] is True
    assert dag["node_count"] >= 6
    assert dag["edge_count"] >= 5

def test_mind_os_45_capability_nodes_have_uid():
    dag = build_execution_dag("validar runtime trader FTMO paper only")

    caps = [n for n in dag["nodes"] if n["node_type"] == "CAPABILITY"]
    assert len(caps) >= 3

    for node in caps:
        assert node["uid"].startswith("CAP_")
        assert node["mode"] == "SHADOW_ONLY"
        assert node["production_allowed"] is False
        assert node["execution_allowed"] is False
        assert node["direct_user_response_allowed"] is False

def test_mind_os_45_final_authority_is_terminal():
    dag = build_execution_dag("crie estratégia de marketing para eldora")

    final = dag["nodes"][-1]
    assert final["node_type"] == "FINAL_AUTHORITY"
    assert final["label"] == "final_authority_required"

    outgoing = [e for e in dag["edges"] if e["from"] == final["node_id"]]
    assert outgoing == []
