from app.modules.usde_core.evidence_registry import EvidenceRegistry

def test_evidence_registry():
    r=EvidenceRegistry()

    e=r.register(
        "EXP001",
        "walk_forward",
        {"accuracy":0.61}
    )

    assert "evidence_id" in e
    assert r.count() >= 1
