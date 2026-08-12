import json
from pathlib import Path

def test_p491f_drive_recursive_paged_inventory():
    inv = json.loads(Path("runtime/drive_absorption/recursive_inventory/drive_recursive_paged_inventory.json").read_text(encoding="utf-8"))
    zips = json.loads(Path("runtime/drive_absorption/zip_inventory/drive_recursive_zip_inventory.json").read_text(encoding="utf-8"))
    queue = json.loads(Path("runtime/drive_absorption/queues/drive_recursive_absorption_queue.json").read_text(encoding="utf-8"))

    assert inv["milestone"] == "P4.91F COMPLETE"
    assert inv["engine"] == "DRIVE_RECURSIVE_PAGED_INVENTORY"
    assert inv["mode"] == "PAGED_FOLDER_WALK_NO_GLOBAL_RECURSIVE"
    assert inv["drive_folder_id"] == "1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"
    assert inv["delete"] == "FORBIDDEN"
    assert inv["move_original"] == "FORBIDDEN"

    assert zips["inventory"] == "DRIVE_RECURSIVE_ZIP_INVENTORY"
    assert queue["queue"] == "DRIVE_RECURSIVE_ABSORPTION_QUEUE"

    for item in queue["items"]:
        assert item["physical_delete"] == "FORBIDDEN"
        assert item["original_preserved"] is True
