import json, hashlib, subprocess
from pathlib import Path
from datetime import datetime, timezone

DRIVE_FOLDER_ID = "1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"
OUT = Path("runtime/drive_absorption")
ABSORBED = OUT / "ledgers" / "drive_absorbed_ledger.json"
INVENTORY = OUT / "inventory" / "drive_live_inventory.json"
ZIP_INV = OUT / "zip_inventory" / "drive_zip_inventory.json"
QUEUE = OUT / "queues" / "drive_absorption_queue.json"

ARCHIVE_EXT = {".zip",".rar",".7z",".tar",".gz",".bz2"}
PROCESS_EXT = {".txt",".json",".csv",".md",".py",".ps1",".yaml",".yml",".xml",".html",".pdf",".doc",".docx",".xls",".xlsx",".ppt",".pptx",".log",".sql",".js",".ts",".tsx",".jsx",".java",".cs",".cpp",".c",".go",".rs",".mq5",".mqh"}

def sha(s):
    return hashlib.sha256(str(s).encode("utf-8", errors="ignore")).hexdigest()

def classify(path):
    s = Path(path).suffix.lower()
    low = str(path).lower()
    if any(x in low for x in ["__pycache__", ".pytest_cache", "node_modules", ".tmp", ".cache"]):
        return "CLEAN_TRASH"
    if s in ARCHIVE_EXT:
        return "ARCHIVE_CONTAINER"
    if s in PROCESS_EXT:
        return "PROCESS"
    if s == "":
        return "REVIEW"
    return "UNKNOWN"

def run_cmd(cmd, timeout=45):
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False
        )
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired as e:
        return 124, e.stdout.decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT"
    except Exception as e:
        return 999, "", repr(e)

def try_rclone_inventory():
    rc, out, err = run_cmd(["rclone", "version"], timeout=10)
    if rc != 0:
        return [], "RCLONE_NOT_FOUND_OR_NOT_WORKING", err

    rc, remotes_out, remotes_err = run_cmd(["rclone", "listremotes"], timeout=10)
    if rc != 0:
        return [], "RCLONE_LISTREMOTES_FAILED", remotes_err

    remotes = [x.strip().rstrip(":") for x in remotes_out.splitlines() if x.strip()]
    if not remotes:
        return [], "NO_RCLONE_REMOTE", ""

    remote = "gdrive" if "gdrive" in remotes else remotes[0]

    # Primeiro tenta inventário limitado sem recursive pesado.
    cmd = ["rclone", "lsjson", f"{remote}:", "--drive-root-folder-id", DRIVE_FOLDER_ID]
    rc, stdout, stderr = run_cmd(cmd, timeout=60)

    if rc == 124:
        return [], "RCLONE_TIMEOUT_NON_RECURSIVE", stderr

    if rc != 0:
        return [], "RCLONE_LSJSON_FAILED", stderr

    try:
        data = json.loads(stdout)
    except Exception as e:
        return [], "RCLONE_JSON_PARSE_FAILED", repr(e)

    rows = []
    for item in data:
        path = item.get("Path") or item.get("Name") or ""
        rows.append({
            "source": "google_drive",
            "drive_folder_id": DRIVE_FOLDER_ID,
            "remote": remote,
            "path": path,
            "name": item.get("Name"),
            "size": item.get("Size"),
            "mime_type": item.get("MimeType"),
            "mod_time": item.get("ModTime"),
            "is_dir": bool(item.get("IsDir")),
            "sha256": sha(path + str(item.get("Size")) + str(item.get("ModTime"))),
            "classification": "FOLDER" if item.get("IsDir") else classify(path)
        })

    return rows, "RCLONE_OK_NON_RECURSIVE_SAFE", ""

existing = []
if ABSORBED.exists():
    try:
        existing = json.loads(ABSORBED.read_text(encoding="utf-8")).get("items", [])
    except Exception:
        existing = []

known_hashes = {x.get("sha256") for x in existing}
inventory, status, error = try_rclone_inventory()

new_items = [x for x in inventory if not x.get("is_dir") and x["sha256"] not in known_hashes]
zip_items = [x for x in inventory if x.get("classification") == "ARCHIVE_CONTAINER"]

queue = []
for item in new_items:
    queue.append({
        **item,
        "status": "PENDING_ABSORPTION",
        "processed": False,
        "knowledge_items": 0,
        "ideas": 0,
        "capabilities_found": 0,
        "physical_delete": "FORBIDDEN",
        "original_preserved": True
    })

inventory_doc = {
    "milestone": "P4.91E2 COMPLETE",
    "engine": "CONTINUOUS_DRIVE_ABSORPTION_ENGINE_RESILIENT_AUDIT",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "drive_folder_id": DRIVE_FOLDER_ID,
    "rclone_status": status,
    "rclone_error": error,
    "mode": "SAFE_NON_RECURSIVE_AUDIT_FIRST",
    "total_drive_items": len(inventory),
    "total_drive_files": len([x for x in inventory if not x.get("is_dir")]),
    "total_drive_folders": len([x for x in inventory if x.get("is_dir")]),
    "new_files": len(new_items),
    "zip_files": len(zip_items),
    "delete": "FORBIDDEN",
    "move_original": "FORBIDDEN",
    "items": inventory,
    "next": "P4.91F DRIVE_RECURSIVE_PAGED_INVENTORY"
}

absorbed_doc = {
    "milestone": "P4.91E2 COMPLETE",
    "ledger": "DRIVE_ABSORBED_LEDGER",
    "items_count": len(existing),
    "items": existing
}

zip_doc = {
    "milestone": "P4.91E2 COMPLETE",
    "inventory": "DRIVE_ZIP_INVENTORY",
    "zip_files_count": len(zip_items),
    "items": zip_items
}

queue_doc = {
    "milestone": "P4.91E2 COMPLETE",
    "queue": "DRIVE_ABSORPTION_QUEUE",
    "items_count": len(queue),
    "items": queue
}

INVENTORY.write_text(json.dumps(inventory_doc, indent=2, ensure_ascii=False), encoding="utf-8")
ABSORBED.write_text(json.dumps(absorbed_doc, indent=2, ensure_ascii=False), encoding="utf-8")
ZIP_INV.write_text(json.dumps(zip_doc, indent=2, ensure_ascii=False), encoding="utf-8")
QUEUE.write_text(json.dumps(queue_doc, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.91E2 COMPLETE",
    "rclone_status": status,
    "drive_folder_id": DRIVE_FOLDER_ID,
    "total_drive_items": len(inventory),
    "total_drive_files": len([x for x in inventory if not x.get("is_dir")]),
    "total_drive_folders": len([x for x in inventory if x.get("is_dir")]),
    "new_files": len(new_items),
    "zip_files": len(zip_items),
    "delete": "FORBIDDEN",
    "next": "P4.91F DRIVE_RECURSIVE_PAGED_INVENTORY"
}, indent=2, ensure_ascii=False))
