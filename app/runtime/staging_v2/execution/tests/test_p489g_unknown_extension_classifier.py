import json
from pathlib import Path

def test_p489g_unknown_extension_classifier():
    report = json.loads(Path("runtime/file_ingestion/unknown_extensions/unknown_extension_classification_report.json").read_text(encoding="utf-8"))
    backlog = json.loads(Path("runtime/file_ingestion/unknown_extensions/parser_backlog.json").read_text(encoding="utf-8"))

    assert report["milestone"] == "P4.89G COMPLETE"
    assert report["engine"] == "UNKNOWN_EXTENSION_CLASSIFIER"
    assert report["mode"] == "CLASSIFY_ONLY"
    assert report["physical_move"] == "NOT_EXECUTED"
    assert report["delete"] == "FORBIDDEN"
    assert report["unknown_total"] >= 0
    assert isinstance(report["summary"], dict)
    assert isinstance(report["classified"], list)

    assert backlog["milestone"] == "P4.89G COMPLETE"
    assert backlog["mode"] == "PLAN_ONLY"
    assert backlog["approval_required"] is True
    assert backlog["items_count"] == len(backlog["items"])
