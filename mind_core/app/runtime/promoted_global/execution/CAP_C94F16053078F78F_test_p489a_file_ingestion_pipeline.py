import json
from pathlib import Path

def test_p489a_file_ingestion_pipeline():
    manifest = json.loads(Path("runtime/file_ingestion/input_manifest.json").read_text(encoding="utf-8"))
    trash = json.loads(Path("runtime/file_ingestion/clean_trash/clean_trash_knowledge.json").read_text(encoding="utf-8"))

    assert manifest["milestone"] == "P4.89A COMPLETE"
    assert manifest["mode"] == "SCAN_AND_CLASSIFY_ONLY"
    assert manifest["physical_move"] == "FORBIDDEN_WITHOUT_APPROVAL"
    assert manifest["governance"] == "P4.83_ENFORCED"
    assert manifest["total_files"] >= 1

    assert "PROCESS" in manifest["queues_count"]
    assert "REVIEW" in manifest["queues_count"]
    assert "ARCHIVE" in manifest["queues_count"]
    assert "CLEAN_TRASH" in manifest["queues_count"]

    assert trash["clean_trash_mode"] == "ACTIVE"
    assert trash["physical_delete"] == "FORBIDDEN"
    assert trash["physical_move"] == "FORBIDDEN_WITHOUT_APPROVAL"
