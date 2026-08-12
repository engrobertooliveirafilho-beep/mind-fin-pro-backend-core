from app.mind.p5_6b6_real_valuation_binder import run_p56b6_healthcheck
from app.mind.p5_6b6_real_valuation_binder.binder import avg

def test_healthcheck():
    assert run_p56b6_healthcheck()["status"]=="P5.6B6_READY"

def test_avg():
    assert avg([10,20,30]) == 20
    assert avg([]) == 0
