from app.mind.p5_5x2_human_family_name_cleaner import run_p55x2_healthcheck
from app.mind.p5_5x2_human_family_name_cleaner.cleaner import bad_human_family_name

def test_p55x2_healthcheck():
    assert run_p55x2_healthcheck()["status"]=="P5.5X2_READY"

def test_bad_human_family_name():
    assert bad_human_family_name("the Berger family of North Dakota")
    assert bad_human_family_name("Berger's son")
    assert bad_human_family_name("Joe Berger")
    assert not bad_human_family_name("Bushwacker")
