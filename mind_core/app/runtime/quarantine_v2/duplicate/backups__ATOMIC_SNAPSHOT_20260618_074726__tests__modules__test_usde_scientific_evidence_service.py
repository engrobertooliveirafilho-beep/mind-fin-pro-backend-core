from app.modules.usde_core.scientific_evidence_service import ScientificEvidenceService

def test_scientific_evidence_service():
    r=ScientificEvidenceService().run(
        {"avg_accuracy":0.55,"red_team_status":"NO_CRITICAL_FLAGS"},
        {"sample_size":100,"baseline":0.5,"seed":42,"experiment_id":"EXP001"}
    )

    assert r["status"]=="COMPLETED"
    assert "evidence_id" in r
