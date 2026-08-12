from app.modules.usde_core.sindy_engine import SINDyEngine

def test_finite_difference():
    d=SINDyEngine().finite_difference(
        [1,2,4,7]
    )

    assert d==[1,2,3]

def test_discover_dynamics():
    r=SINDyEngine().discover_dynamics(
        [1,2,4,8,16]
    )

    assert "equation" in r
    assert len(r["coefficients"])==1
