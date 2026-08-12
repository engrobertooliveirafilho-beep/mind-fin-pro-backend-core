from app.mind.p5_5x6_cross_duplicate_cleaner import run_p55x6_healthcheck
from app.mind.p5_5x6_cross_duplicate_cleaner.cleaner import is_cross_fragment, canon_name

def test_p55x6_healthcheck():
    assert run_p55x6_healthcheck()["status"]=="P5.5X6_READY"

def test_cross_fragment():
    assert is_cross_fragment("Bruce Hunt. BRUISER X BUSHWACKER")
    assert not is_cross_fragment("Bushwacker")

def test_canon_name():
    assert canon_name(" Bushwacker ")=="bushwacker"
