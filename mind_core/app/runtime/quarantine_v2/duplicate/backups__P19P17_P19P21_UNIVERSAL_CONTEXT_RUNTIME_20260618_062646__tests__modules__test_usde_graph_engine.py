from app.modules.usde_core.graph_engine import GraphEngine

def test_graph_creation():
    events=[
        {"id":1,"values":[1,2,3]},
        {"id":2,"values":[2,3,4]}
    ]

    g=GraphEngine().cooccurrence_graph(events)

    assert "1" in g
    assert "2" in g

def test_degree_centrality():
    graph={
        "1":{"2":1,"3":1},
        "2":{"1":1}
    }

    c=GraphEngine().degree_centrality(graph)

    assert c["1"]==2

def test_weighted_degree():
    graph={
        "1":{"2":5,"3":2}
    }

    w=GraphEngine().weighted_degree(graph)

    assert w["1"]==7
