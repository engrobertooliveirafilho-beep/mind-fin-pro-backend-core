from app.mind.p5_5u_real_result_claim_extractor import run_p55u_healthcheck
from app.mind.p5_5u_real_result_claim_extractor.extractor import extract_claims

def test_p55u_healthcheck():
    assert run_p55u_healthcheck()["status"]=="P5.5U_READY"

def test_extract_claims():
    c=extract_claims("Bushwacker 13/6 ABBI pedigree sire dam PBR score 46.25 semen auction 2006")
    assert "13/6" in c["patterns"]["registry_numbers"]
    assert c["has_pedigree_signal"] is True
    assert c["has_market_signal"] is True
    assert c["claim_strength"] > 40
