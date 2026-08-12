import json
from app.mind.p5_5a_bovine_sports_genetics.runtime import run_healthcheck
from app.mind.p5_5a_bovine_sports_genetics.core import P55AOrchestrator, BullIdentity, Evidence, BiomechanicsScore
from app.mind.p5_5a_bovine_sports_genetics.engines import BullDigitalJudgeEngine, BullVideoBiomechanicsEngine

def test_p55a_healthcheck():
    h = run_healthcheck()
    assert h["status"] == "P5.5A_READY"
    assert h["modules_count"] == 13
    assert h["agents_count"] == 13

def test_identity_key_stable():
    a = BullIdentity(official_name="Bushwacker", registry_number="13/6", birth_year=2006)
    b = BullIdentity(official_name=" bushwacker ", registry_number="13/6", birth_year=2006)
    assert a.identity_key() == b.identity_key()

def test_evidence_hash_and_band():
    e = Evidence(source_url="https://example.com", confidence_score=91).to_record()
    assert e["validation_status"] == "highly_reliable"
    assert len(e["evidence_hash"]) == 64

def test_biomechanics_composite():
    s = BullVideoBiomechanicsEngine().score({"initial_explosion":90,"unpredictability":80,"difficulty":85,"kick_frequency":70,"kick_amplitude":80,"angular_velocity":75,"consistency":88})
    assert s["biomechanics_score"] > 0
    assert s["buckoff_pressure_score"] == 85

def test_digital_judge_error():
    r = BullDigitalJudgeEngine().compare(45, 43)
    assert r["absolute_error"] == 2
