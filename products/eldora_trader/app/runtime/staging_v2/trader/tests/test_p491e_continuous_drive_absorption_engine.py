import json
from pathlib import Path

def test_p491e_continuous_drive_absorption_engine():
    inv = json.loads(Path("runtime/drive_absorption/inventory/drive_live_inventory.json").read_text(encoding="utf-8"))
    ledger = json.loads(Path("runtime/drive_absorption/ledgers/drive_absorbed_ledger.json").read_text(encoding="utf-8"))
    zips = json.loads(Path("runtime/drive_absorption/zip_inventory/drive_zip_inventory.json").read_text(encoding="utf-8"))
    queue = json.loads(Path("runtime/drive_absorption/queues/drive_absorption_queue.json").read_text(encoding="utf-8"))

    assert inv["milestone"] == "P4.91E COMPLETE"
    assert inv["engine"] == "CONTINUOUS_DRIVE_ABSORPTION_ENGINE"
    assert inv["drive_folder_id"] == "1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"
    assert inv["delete"] == "FORBIDDEN"
    assert inv["move_original"] == "FORBIDDEN"

    assert ledger["ledger"] == "DRIVE_ABSORBED_LEDGER"
    assert zips["inventory"] == "DRIVE_ZIP_INVENTORY"
    assert queue["queue"] == "DRIVE_ABSORPTION_QUEUE"

    for item in queue["items"]:
        assert item["physical_delete"] == "FORBIDDEN"
        assert item["original_preserved"] is True
