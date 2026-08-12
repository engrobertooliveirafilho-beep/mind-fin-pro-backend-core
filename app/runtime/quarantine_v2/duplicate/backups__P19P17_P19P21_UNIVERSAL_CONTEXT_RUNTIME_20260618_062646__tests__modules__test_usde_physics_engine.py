from app.modules.usde_core.physics_engine import PhysicsEngine

def test_random_walk():
    r=PhysicsEngine().random_walk_metrics(
        [1,2,3,4,5]
    )

    assert r["steps"]==4

def test_poisson():
    r=PhysicsEngine().poisson_process_score(
        [1,2,3,2,1]
    )

    assert r["lambda"]>0

def test_criticality():
    r=PhysicsEngine().criticality_proxy(
        [1,5,2,8,3,10]
    )

    assert 0<=r["criticality"]<=1
