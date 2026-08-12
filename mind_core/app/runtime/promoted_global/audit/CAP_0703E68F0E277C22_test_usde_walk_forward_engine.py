from app.modules.usde_core.walk_forward_engine import WalkForwardEngine

def predictor(train):
    return train[-1]["values"]

def test_walk_forward():
    events=[
        {"id":1,"values":[1,2,3]},
        {"id":2,"values":[2,3,4]},
        {"id":3,"values":[3,4,5]},
        {"id":4,"values":[4,5,6]},
        {"id":5,"values":[5,6,7]},
        {"id":6,"values":[6,7,8]}
    ]

    r=WalkForwardEngine().evaluate(events,predictor)

    assert r["evaluations"]>0
    assert 0<=r["avg_accuracy"]<=1
