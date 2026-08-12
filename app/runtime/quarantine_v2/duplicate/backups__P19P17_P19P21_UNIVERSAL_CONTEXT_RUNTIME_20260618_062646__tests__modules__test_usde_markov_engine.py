from app.modules.usde_core.markov_engine import MarkovEngine

def test_markov_matrix():
    events=[
        {"id":1,"values":[1,2]},
        {"id":2,"values":[2,3]},
        {"id":3,"values":[1,3]}
    ]

    m=MarkovEngine().transition_matrix(events)

    assert "1" in m
    assert "2" in m

def test_markov_persistence():
    events=[
        {"id":1,"values":[1,2]},
        {"id":2,"values":[1,2]},
        {"id":3,"values":[1,3]}
    ]

    p=MarkovEngine().persistence_score(events)

    assert "1" in p
