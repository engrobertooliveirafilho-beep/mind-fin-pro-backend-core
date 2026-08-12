import json
from pathlib import Path

def test_p489_full_repository_intelligence_report():
    p = Path("runtime/repository_intelligence/full_repository_intelligence_report.json")
    assert p.exists()

    data = json.loads(p.read_text(encoding="utf-8"))

    assert data["milestone"] == "P4.89 COMPLETE"
    assert data["engine"] == "FULL_REPOSITORY_INTELLIGENCE"
    assert data["mode"] == "READ_ONLY_INTELLIGENCE"
    assert data["governance"] == "P4.83_ENFORCED"

    assert data["architecture"]["app_files"] >= 1
    assert data["architecture"]["runtime_files"] >= 1
    assert data["architecture"]["test_files"] >= 1

    assert data["capability_status"]["prioritization"] is True
    assert data["capability_status"]["governance_gate"] is True
    assert data["capability_status"]["reconstruction"] is True
    assert data["capability_status"]["knowledge_graph"] is True
    assert data["capability_status"]["orphan_recovery"] is True
    assert data["capability_status"]["capability_merge"] is True
    assert data["capability_status"]["technical_gap_detector"] is True

    assert data["readiness"]["ready_for_p490"] is True
    assert data["next"] == "P4.90 SOVEREIGN TECHNICAL CAPACITY CERTIFICATION"
