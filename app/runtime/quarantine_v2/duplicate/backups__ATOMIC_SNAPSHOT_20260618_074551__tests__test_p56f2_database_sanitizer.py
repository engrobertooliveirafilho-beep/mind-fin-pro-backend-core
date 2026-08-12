from app.mind.p5_6f2_database_sanitizer import run_p56f2_healthcheck
from app.mind.p5_6f2_database_sanitizer.sanitizer import is_bad

def test_healthcheck():
    assert run_p56f2_healthcheck()["status"]=="P5.6F2_READY"

def test_bad_names():
    assert is_bad("ride YouTube")
    assert is_bad("auction sale price")
    assert not is_bad("Bushwacker")
    assert not is_bad("Little Yellow Jacket")
