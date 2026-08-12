from app.mind.p5_6b8_real_country_ranking_recalculator import run_p56b8_healthcheck
from app.mind.p5_6b8_real_country_ranking_recalculator.recalculator import avg

def test_healthcheck():
    assert run_p56b8_healthcheck()["status"]=="P5.6B8_READY"

def test_avg():
    assert avg([1,2,3]) == 2
    assert avg([]) == 0
