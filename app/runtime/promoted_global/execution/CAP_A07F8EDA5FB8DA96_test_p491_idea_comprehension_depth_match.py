import json
from pathlib import Path

def test_p491_idea_comprehension_depth_match():
    report = json.loads(Path("runtime/idea_intelligence/idea_comprehension_report.json").read_text(encoding="utf-8"))
    depth = json.loads(Path("runtime/idea_intelligence/module_depth_match_report.json").read_text(encoding="utf-8"))
    backlog = json.loads(Path("runtime/idea_intelligence/idea_resolution_backlog.json").read_text(encoding="utf-8"))

    assert report["milestone"] == "P4.91 COMPLETE"
    assert report["engine"] == "IDEA_COMPREHENSION_ENGINE"
    assert report["mode"] == "ANALYSIS_ONLY"
    assert report["ideas_comprehended"] == len(report["items"])

    assert depth["milestone"] == "P4.91 COMPLETE"
    assert depth["engine"] == "MODULE_DEPTH_MATCH_ENGINE"
    assert depth["mode"] == "ANALYSIS_ONLY"

    assert backlog["milestone"] == "P4.91 COMPLETE"
    assert backlog["implementation"] == "FORBIDDEN"
    assert backlog["approval_required"] is True
    assert backlog["items_count"] == len(backlog["items"])
