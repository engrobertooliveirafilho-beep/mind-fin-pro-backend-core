from app.mind.p5_5x5_final_phrase_cleaner import run_p55x5_healthcheck
from app.mind.p5_5x5_final_phrase_cleaner.cleaner import bad_final_phrase

def test_p55x5_healthcheck():
    assert run_p55x5_healthcheck()["status"]=="P5.5X5_READY"

def test_bad_final_phrase():
    assert bad_final_phrase("the Professional Bull Riders")
    assert bad_final_phrase("to futurity champion")
    assert bad_final_phrase("the great Party Girl female")
    assert not bad_final_phrase("Bushwacker")
