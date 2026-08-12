from app.mind.p5_6f1_animal_discovery_engine import run_p56f1_healthcheck
from app.mind.p5_6f1_animal_discovery_engine.engine import clean_name, candidate_hash

def test_healthcheck():
    assert run_p56f1_healthcheck()["status"]=="P5.6F1_READY"

def test_clean_name():
    assert clean_name("Bushwacker bull!") == "Bushwacker"

def test_hash():
    assert candidate_hash("Bushwacker") == candidate_hash("bushwacker")
