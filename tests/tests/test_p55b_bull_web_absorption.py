from app.mind.p5_5b_bull_web_absorption import run_p55b_healthcheck
from app.mind.p5_5b_bull_web_absorption.engine import BullWebAbsorptionEngine

def test_p55b_healthcheck():
    h=run_p55b_healthcheck()
    assert h["status"]=="P5.5B_READY"
    assert h["seed_queries"]>=8

def test_p55b_evidence_score_and_dedupe():
    e=BullWebAbsorptionEngine()
    r=e.normalize_result({"url":"https://pbr.com/example","source_type":"PBR","title":"Bull score","snippet":"official"})
    assert r["confidence_score"]>=75
    assert len(e.dedupe([r,r]))==1

def test_p55b_claim_extraction():
    e=BullWebAbsorptionEngine()
    c=e.extract_candidate_animal_claims("Bull 13/6 born 2006 scored 46.25")
    assert "13/6" in c["possible_registry_number"]
    assert "2006" in c["possible_year"]
