from app.mind.p5_5f_bull_candidate_ingestion import run_p55f_healthcheck
from app.mind.p5_5f_bull_candidate_ingestion.ingestion import identity_key, REAL_BULL_CANDIDATES, BullCandidateIngestion

def test_p55f_healthcheck():
    h=run_p55f_healthcheck()
    assert h["status"]=="P5.5F_READY"
    assert h["candidate_count"]>=6

def test_identity_key_stable():
    a={"official_name":" Bushwacker ","registry_number":"13/6","birth_year":2006}
    b={"official_name":"bushwacker","registry_number":"13/6","birth_year":2006}
    assert identity_key(a)==identity_key(b)

def test_prepare_without_remote():
    w=BullCandidateIngestion(url="https://example.supabase.co", key="fake")
    p=w.prepare(REAL_BULL_CANDIDATES[0])
    assert len(p["identity_key"])==64
