from app.mind.p5_5x3_org_fragment_cleaner import run_p55x3_healthcheck
from app.mind.p5_5x3_org_fragment_cleaner.cleaner import bad_org_fragment_name

def test_p55x3_healthcheck():
    assert run_p55x3_healthcheck()["status"]=="P5.5X3_READY"

def test_bad_org_fragment_name():
    assert bad_org_fragment_name("PBR")
    assert bad_org_fragment_name("contacting Hookin' W Ranch. Prices")
    assert not bad_org_fragment_name("Bushwacker")
