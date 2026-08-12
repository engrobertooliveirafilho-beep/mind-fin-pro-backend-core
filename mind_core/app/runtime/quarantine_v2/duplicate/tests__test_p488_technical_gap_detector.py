import json
from pathlib import Path

def test_p488_technical_gap_detector_plan_only():
    report = json.loads(Path("runtime/technical_gaps/technical_gap_report.json").read_text(encoding="utf-8"))
    backlog = json.loads(Path("runtime/technical_gaps/gap_resolution_backlog.json").read_text(encoding="utf-8"))

    assert report["milestone"] == "P4.88 COMPLETE"
    assert report["engine"] == "TECHNICAL_GAP_DETECTOR"
    assert report["mode"] == "PLAN_ONLY"
    assert report["governance"] == "P4.83_ENFORCED"
    assert "full_repository_intelligence" in report["desired_capabilities"]
    assert "sovereign_certification" in report["desired_capabilities"]
    assert report["gaps_count"] >= 2

    assert backlog["milestone"] == "P4.88 COMPLETE"
    assert backlog["automatic_execution"] == "FORBIDDEN"
    assert backlog["approval_required"] is True
    assert backlog["items_count"] == len(backlog["items"])

    for item in backlog["items"]:
        assert item["approval_status"] == "PENDING_APPROVAL"
        assert item["execution_status"] == "BLOCKED_BY_P4.83_GATE"
