from app.mind.p5_5m_identity_merge_resolver import run_p55m_healthcheck
from app.mind.p5_5m_identity_merge_resolver.resolver import canon_name, canonical_choice

def test_p55m_healthcheck():
    assert run_p55m_healthcheck()["status"]=="P5.5M_READY"

def test_canon_name():
    assert canon_name(" Bushwacker  ")=="bushwacker"

def test_canonical_choice_prefers_confidence():
    rows=[{"id":"a","confidence_score":40},{"id":"b","confidence_score":80}]
    assert canonical_choice(rows)["id"]=="b"
