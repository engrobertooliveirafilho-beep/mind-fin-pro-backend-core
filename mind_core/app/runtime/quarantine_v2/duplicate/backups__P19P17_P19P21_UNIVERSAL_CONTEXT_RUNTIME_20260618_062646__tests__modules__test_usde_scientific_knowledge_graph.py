from app.modules.usde_core.scientific_knowledge_graph import ScientificKnowledgeGraph

def test_graph_nodes():
    g=ScientificKnowledgeGraph()

    g.add_node("H1","hypothesis")
    g.add_node("E1","experiment")

    assert g.summary()["nodes"]==2

def test_graph_edges():
    g=ScientificKnowledgeGraph()

    g.add_node("H1","hypothesis")
    g.add_node("E1","experiment")

    g.add_edge(
        "H1",
        "E1",
        "tested_by"
    )

    assert g.summary()["edges"]==1

def test_neighbors():
    g=ScientificKnowledgeGraph()

    g.add_node("A","x")
    g.add_node("B","y")

    g.add_edge("A","B","rel")

    assert "B" in g.neighbors("A")
