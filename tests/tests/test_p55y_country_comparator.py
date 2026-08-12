from app.mind.p5_5y_country_comparator import run_p55y_healthcheck
from app.mind.p5_5y_country_comparator.comparator import avg

def test_p55y_healthcheck():
    assert run_p55y_healthcheck()["status"]=="P5.5Y_READY"

def test_avg():
    assert avg([10,20,30])==20
    assert avg([])==0
