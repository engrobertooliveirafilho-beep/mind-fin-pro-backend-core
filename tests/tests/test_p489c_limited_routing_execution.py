import json
from pathlib import Path

def test_p489c_limited_routing_execution():
    ledger = json.loads(Path("runtime/file_ingestion/executed_routing/p489c_execution_ledger.json").read_text(encoding="utf-8"))
    rollback = json.loads(Path("runtime/file_ingestion/executed_routing/p489c_rollback_manifest.json").read_text(encoding="utf-8"))

    assert ledger["milestone"] == "P4.89C COMPLETE"
    assert ledger["mode"] == "LIMITED_PHYSICAL_MOVE"
    assert ledger["delete"] == "FORBIDDEN"
    assert set(ledger["allowed_queues"]) == {"ARCHIVE", "CLEAN_TRASH"}

    for item in ledger["executed"]:
        assert item["queue"] in ["ARCHIVE", "CLEAN_TRASH"]
        assert item["moved"] is True
        assert item["delete"] is False
        assert not item["source"].startswith(("app/", "tests/", "tools/", "runtime/"))

    assert rollback["rollback_available"] is True
    assert rollback["items_count"] == ledger["executed_count"]
