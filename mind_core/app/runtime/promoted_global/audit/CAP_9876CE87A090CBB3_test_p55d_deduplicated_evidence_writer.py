from app.mind.p5_5d_deduplicated_evidence_writer import run_p55d_healthcheck
from app.mind.p5_5d_deduplicated_evidence_writer.writer import stable_hash, DeduplicatedEvidenceWriter

def test_p55d_healthcheck():
    assert run_p55d_healthcheck()["status"]=="P5.5D_READY"

def test_stable_hash_is_equal_for_same_payload():
    a={"source_url":"https://pbr.com","source_type":"PBR","title":"Seed","raw_payload":{"x":1}}
    b={"title":"Seed","source_type":"PBR","raw_payload":{"x":1},"source_url":"https://pbr.com"}
    assert stable_hash(a)==stable_hash(b)

def test_prepare_generates_hash_without_remote_call():
    w=DeduplicatedEvidenceWriter(url="https://example.supabase.co", key="fake")
    p=w.prepare({"source_url":"https://pbr.com","source_type":"PBR","title":"Seed"})
    assert len(p["evidence_hash"])==64
    assert p["validation_status"]=="provisional"
