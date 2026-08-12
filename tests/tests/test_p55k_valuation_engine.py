from app.mind.p5_5k_valuation_engine import run_p55k_healthcheck
from app.mind.p5_5k_valuation_engine.engine import valuation_score

def test_p55k_healthcheck():
    assert run_p55k_healthcheck()["status"]=="P5.5K_READY"

def test_valuation_score_range():
    assert valuation_score(100,100,10,10,100)==100
    assert valuation_score(0,0,0,0,0)==0
