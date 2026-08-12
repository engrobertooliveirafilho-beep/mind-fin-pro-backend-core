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
    return hashlib.sha256(str(s).encode("utf-8")).hexdigest()

def classify(path):
    p = Path(path)
    s = p.suffix.lower()
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

def try_rclone_inventory():
    rclone = subprocess.run(["where", "rclone"], shell=True, capture_output=True, text=True)
    if rclone.returncode != 0:
        return [], "RCLONE_NOT_FOUND"

    remotes = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
    if remotes.returncode != 0:
        return [], "RCLONE_LISTREMOTES_FAILED"

    remote_names = [x.strip().rstrip(":") for x in remotes.stdout.splitlines() if x.strip()]
    if not remote_names:
        return [], "NO_RCLONE_REMOTE"

    remote = remote_names[0]
    cmd = ["rclone", "lsjson", f"{remote}:", "--drive-root-folder-id", DRIVE_FOLDER_ID, "--recursive"]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if out.returncode != 0:
        return [], "RCLONE_LSJSON_FAILED"

    try:
        data = json.loads(out.stdout)
    except Exception:
        return [], "RCLONE_JSON_PARSE_FAILED"

    rows = []
    for item in data:
        if item.get("IsDir"):
            continue
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
            "sha256": sha(path + str(item.get("Size")) + str(item.get("ModTime"))),
            "classification": classify(path)
        })
    return rows, "RCLONE_OK"

existing = []
if ABSORBED.exists():
    try:
        existing = json.loads(ABSORBED.read_text(encoding="utf-8")).get("items", [])
    except Exception:
        existing = []

known_hashes = {x.get("sha256") for x in existing}

inventory, status = try_rclone_inventory()

new_items = [x for x in inventory if x["sha256"] not in known_hashes]
zip_items = [x for x in inventory if x["classification"] == "ARCHIVE_CONTAINER"]

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
    "milestone": "P4.91E COMPLETE",
    "engine": "CONTINUOUS_DRIVE_ABSORPTION_ENGINE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "drive_folder_id": DRIVE_FOLDER_ID,
    "rclone_status": status,
    "mode": "LIVE_AUDIT_IF_RCLONE_AVAILABLE",
    "total_drive_files": len(inventory),
    "new_files": len(new_items),
    "zip_files": len(zip_items),
    "delete": "FORBIDDEN",
    "move_original": "FORBIDDEN",
    "next": "P4.91F DRIVE_ZIP_RECURSIVE_ABSORPTION"
}

absorbed_doc = {
    "milestone": "P4.91E COMPLETE",
    "ledger": "DRIVE_ABSORBED_LEDGER",
    "items_count": len(existing),
    "items": existing,
    "note": "Ledger preservado; novos arquivos ficam na fila até processamento certificado."
}

zip_doc = {
    "milestone": "P4.91E COMPLETE",
    "inventory": "DRIVE_ZIP_INVENTORY",
    "zip_files_count": len(zip_items),
    "items": zip_items
}

queue_doc = {
    "milestone": "P4.91E COMPLETE",
    "queue": "DRIVE_ABSORPTION_QUEUE",
    "items_count": len(queue),
    "items": queue
}

INVENTORY.write_text(json.dumps({**inventory_doc, "items": inventory}, indent=2, ensure_ascii=False), encoding="utf-8")
ABSORBED.write_text(json.dumps(absorbed_doc, indent=2, ensure_ascii=False), encoding="utf-8")
ZIP_INV.write_text(json.dumps(zip_doc, indent=2, ensure_ascii=False), encoding="utf-8")
QUEUE.write_text(json.dumps(queue_doc, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.91E COMPLETE",
    "rclone_status": status,
    "drive_folder_id": DRIVE_FOLDER_ID,
    "total_drive_files": len(inventory),
    "new_files": len(new_items),
    "zip_files": len(zip_items),
    "delete": "FORBIDDEN",
    "next": "P4.91F DRIVE_ZIP_RECURSIVE_ABSORPTION"
}, indent=2, ensure_ascii=False))
