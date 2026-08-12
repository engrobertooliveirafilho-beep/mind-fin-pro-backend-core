import json
from pathlib import Path

def test_p487_capability_merge_engine_plan_only():
    report = json.loads(Path("runtime/capability_merge/capability_merge_report.json").read_text(encoding="utf-8"))
    plan = json.loads(Path("runtime/capability_merge/consolidation_plan.json").read_text(encoding="utf-8"))

    assert report["milestone"] == "P4.87 COMPLETE"
    assert report["engine"] == "CAPABILITY_MERGE_ENGINE"
    assert report["mode"] == "PLAN_ONLY"
    assert report["governance"] == "P4.83_ENFORCED"
    assert report["records_scanned"] >= 1
    assert "overlaps" in report
    assert "semantic_overlaps" in report

    assert plan["milestone"] == "P4.87 COMPLETE"
    assert plan["automatic_merge"] == "FORBIDDEN"
    assert plan["approval_required"] is True
    assert "require_manual_approval" in plan["steps"]
