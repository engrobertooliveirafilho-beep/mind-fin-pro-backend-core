from app.mind.p5_5x4_strict_animal_name_normalizer import run_p55x4_healthcheck
from app.mind.p5_5x4_strict_animal_name_normalizer.normalizer import should_delete, normalized_name

def test_p55x4_healthcheck():
    assert run_p55x4_healthcheck()["status"]=="P5.5X4_READY"

def test_should_delete():
    assert should_delete("Barker Bulls in partnership with Hookin'")
    assert should_delete("appointment on weekends only. t. SIRE")
    assert not should_delete("Bushwacker")

def test_normalized_name():
    assert normalized_name("Red Wolf DAM")=="Red Wolf"
    assert normalized_name("Whitewater Skoal")=="Whitewater Skoal"
