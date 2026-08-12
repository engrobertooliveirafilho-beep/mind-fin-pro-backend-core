from app.mind.p5_5r_claim_to_entity_promoter import run_p55r_healthcheck
from app.mind.p5_5r_claim_to_entity_promoter.promoter import detect_animals, identity_key

def test_p55r_healthcheck():
    assert run_p55r_healthcheck()["status"]=="P5.5R_READY"

def test_detect_animals():
    assert "Bushwacker" in detect_animals("PBR Bushwacker official score")

def test_identity_key_stable():
    assert identity_key(" Bushwacker ") == identity_key("bushwacker")
