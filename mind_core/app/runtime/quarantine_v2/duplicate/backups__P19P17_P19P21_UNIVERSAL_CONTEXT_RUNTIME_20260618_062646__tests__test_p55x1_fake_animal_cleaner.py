from app.mind.p5_5x1_fake_animal_cleaner import run_p55x1_healthcheck
from app.mind.p5_5x1_fake_animal_cleaner.cleaner import bad_name

def test_p55x1_healthcheck():
    assert run_p55x1_healthcheck()["status"]=="P5.5X1_READY"

def test_bad_name():
    assert bad_name("dam offspring")
    assert bad_name("Competition Stats http")
    assert not bad_name("Bushwacker")
