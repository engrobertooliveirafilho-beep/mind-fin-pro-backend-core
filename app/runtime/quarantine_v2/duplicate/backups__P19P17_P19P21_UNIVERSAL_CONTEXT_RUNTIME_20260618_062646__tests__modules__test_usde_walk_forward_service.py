from app.modules.usde_core.walk_forward_service import WalkForwardService

def test_walk_forward_service():
    events=[
        {"id":1,"values":[1,2]},
        {"id":2,"values":[2,3]},
        {"id":3,"values":[3,4]},
        {"id":4,"values":[4,5]},
        {"id":5,"values":[5,6]}
    ]

    r=WalkForwardService().run(events)

    assert r["status"]=="COMPLETED"
    assert r["evaluations"] > 0
