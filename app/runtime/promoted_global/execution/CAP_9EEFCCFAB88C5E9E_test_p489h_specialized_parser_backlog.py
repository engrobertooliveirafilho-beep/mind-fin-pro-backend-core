import json
from pathlib import Path

def test_p489h_specialized_parser_backlog():
    backlog = json.loads(Path("runtime/file_ingestion/specialized_parsers/specialized_parser_backlog.json").read_text(encoding="utf-8"))
    report = json.loads(Path("runtime/file_ingestion/specialized_parsers/unknown_reclassification_report.json").read_text(encoding="utf-8"))

    assert backlog["milestone"] == "P4.89H COMPLETE"
    assert backlog["mode"] == "PLAN_ONLY"
    assert backlog["physical_move"] == "NOT_EXECUTED"
    assert backlog["delete"] == "FORBIDDEN"
    assert backlog["items_count"] >= 0
    assert isinstance(backlog["parser_summary"], dict)

    assert report["milestone"] == "P4.89H COMPLETE"
    assert report["engine"] == "UNKNOWN_RECLASSIFICATION_ENGINE"
    assert report["mode"] == "CLASSIFY_ONLY"
    assert isinstance(report["summary"], dict)
