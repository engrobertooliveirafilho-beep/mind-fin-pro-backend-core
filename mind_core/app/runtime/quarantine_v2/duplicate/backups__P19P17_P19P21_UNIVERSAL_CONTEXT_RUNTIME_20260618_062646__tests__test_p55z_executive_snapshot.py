from app.mind.p5_5z_executive_snapshot import run_p55z_healthcheck

def test_p55z_healthcheck():
    assert run_p55z_healthcheck()["status"]=="P5.5Z_READY"
