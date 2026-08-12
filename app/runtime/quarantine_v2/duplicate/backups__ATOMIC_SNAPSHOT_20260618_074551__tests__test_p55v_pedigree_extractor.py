from app.mind.p5_5v_pedigree_extractor import run_p55v_healthcheck
from app.mind.p5_5v_pedigree_extractor.extractor import extract_pedigree_claims

def test_p55v_healthcheck():
    assert run_p55v_healthcheck()["status"]=="P5.5V_READY"

def test_extract_pedigree_claims():
    c=extract_pedigree_claims("Bushwacker sire: Whitewater Skoal dam: Lady Luck")
    assert any(x["relation"]=="sire" for x in c)
    assert any(x["relation"]=="dam" for x in c)
