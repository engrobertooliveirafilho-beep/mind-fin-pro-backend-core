from app.mind.p5_6b7_real_ranking_api import run_p56b7_healthcheck

def test_healthcheck():
    assert run_p56b7_healthcheck()["status"]=="P5.6B7_READY"
