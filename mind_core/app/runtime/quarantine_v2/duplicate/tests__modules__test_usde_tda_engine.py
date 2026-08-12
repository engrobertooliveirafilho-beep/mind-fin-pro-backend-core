from app.modules.usde_core.tda_engine import TDAEngine

def test_tda_persistence():
    events=[
        {"id":1,"values":[1,2,3]},
        {"id":2,"values":[2,3,4]},
        {"id":3,"values":[3,4,5]}
    ]

    r=TDAEngine().persistence_score(events)

    assert r["features"]>0

def test_tda_betti_proxy():
    events=[
        {"id":1,"values":[1,2]},
        {"id":2,"values":[2,3]}
    ]

    r=TDAEngine().betti_proxy(events)

    assert "betti_0_proxy" in r
    assert "betti_1_proxy" in r
