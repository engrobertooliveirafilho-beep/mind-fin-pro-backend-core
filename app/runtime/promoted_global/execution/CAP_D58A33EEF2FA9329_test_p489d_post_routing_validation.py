import json
from pathlib import Path

def test_p489d_post_routing_validation():
    report = json.loads(Path("runtime/file_ingestion/validation/post_routing_validation_report.json").read_text(encoding="utf-8"))

    assert report["milestone"] == "P4.89D COMPLETE"
    assert report["mode"] == "VALIDATION_ONLY"
    assert report["physical_move"] == "NOT_EXECUTED_IN_THIS_STAGE"
    assert report["delete"] == "FORBIDDEN"
    assert report["missing_targets"] == 0
    assert report["errors_count"] == 0
    assert report["rollback_available"] is True
    assert report["ready_for_p490"] is True
