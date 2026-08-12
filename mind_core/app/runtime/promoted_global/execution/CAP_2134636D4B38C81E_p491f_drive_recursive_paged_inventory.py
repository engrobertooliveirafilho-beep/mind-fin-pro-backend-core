import json, hashlib, subprocess, collections
from pathlib import Path
from datetime import datetime, timezone

DRIVE_FOLDER_ID = "1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"
BASE = Path("runtime/drive_absorption")
PREV = BASE / "inventory" / "drive_live_inventory.json"
OUT = BASE / "recursive_inventory" / "drive_recursive_paged_inventory.json"
ZIP_OUT = BASE / "zip_inventory" / "drive_recursive_zip_inventory.json"
QUEUE_OUT = BASE / "queues" / "drive_recursive_absorption_queue.json"

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

def run_cmd(cmd, timeout=35):
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
        return 124, e.stdout if isinstance(e.stdout, str) else "", "TIMEOUT"
    except Exception as e:
        return 999, "", repr(e)

def get_remote():
    rc, out, err = run_cmd(["rclone", "listremotes"], timeout=10)
    remotes = [x.strip().rstrip(":") for x in out.splitlines() if x.strip()]
    if "gdrive" in remotes:
        return "gdrive"
    return remotes[0] if remotes else None

remote = get_remote()
items = []
errors = []
folders_seen = set()
queue = collections.deque()

if remote is None:
    status = "NO_RCLONE_REMOTE"
else:
    status = "RCLONE_PAGED_STARTED"
    queue.append({"path": "", "depth": 0, "folder_id": DRIVE_FOLDER_ID})

MAX_FOLDERS = 500
MAX_DEPTH = 10

while queue and len(folders_seen) < MAX_FOLDERS:
    cur = queue.popleft()
    folder_path = cur["path"]
    depth = cur["depth"]

    key = folder_path or "ROOT"
    if key in folders_seen:
        continue
    folders_seen.add(key)

    if depth > MAX_DEPTH:
        errors.append({"folder": folder_path, "error": "MAX_DEPTH_REACHED"})
        continue

    remote_path = f"{remote}:{folder_path}" if folder_path else f"{remote}:"

    cmd = ["rclone", "lsjson", remote_path, "--drive-root-folder-id", DRIVE_FOLDER_ID]
    rc, stdout, stderr = run_cmd(cmd, timeout=45)

    if rc != 0:
        errors.append({"folder": folder_path, "returncode": rc, "error": stderr[:1000]})
        continue

    try:
        data = json.loads(stdout)
    except Exception as e:
        errors.append({"folder": folder_path, "error": "JSON_PARSE_FAILED", "detail": repr(e)})
        continue

    for obj in data:
        name = obj.get("Name") or obj.get("Path") or ""
        rel = f"{folder_path}/{name}".strip("/") if folder_path else name
        is_dir = bool(obj.get("IsDir"))

        row = {
            "source": "google_drive",
            "drive_folder_id": DRIVE_FOLDER_ID,
            "remote": remote,
            "path": rel,
            "name": name,
            "size": obj.get("Size"),
            "mime_type": obj.get("MimeType"),
            "mod_time": obj.get("ModTime"),
            "is_dir": is_dir,
            "depth": depth,
            "sha256": sha(rel + str(obj.get("Size")) + str(obj.get("ModTime"))),
            "classification": "FOLDER" if is_dir else classify(rel)
        }
        items.append(row)

        if is_dir:
            queue.append({"path": rel, "depth": depth + 1})

files = [x for x in items if not x["is_dir"]]
folders = [x for x in items if x["is_dir"]]
zips = [x for x in files if x["classification"] == "ARCHIVE_CONTAINER"]

absorption_queue = [
    {
        **x,
        "status": "PENDING_ABSORPTION",
        "processed": False,
        "physical_delete": "FORBIDDEN",
        "original_preserved": True
    }
    for x in files
]

doc = {
    "milestone": "P4.91F COMPLETE",
    "engine": "DRIVE_RECURSIVE_PAGED_INVENTORY",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "drive_folder_id": DRIVE_FOLDER_ID,
    "remote": remote,
    "status": status,
    "mode": "PAGED_FOLDER_WALK_NO_GLOBAL_RECURSIVE",
    "delete": "FORBIDDEN",
    "move_original": "FORBIDDEN",
    "max_folders": MAX_FOLDERS,
    "max_depth": MAX_DEPTH,
    "folders_walked": len(folders_seen),
    "items_total": len(items),
    "files_total": len(files),
    "folders_total": len(folders),
    "zip_files": len(zips),
    "errors_count": len(errors),
    "errors": errors,
    "items": items,
    "next": "P4.91G DRIVE_ZIP_RECURSIVE_ABSORPTION"
}

zip_doc = {
    "milestone": "P4.91F COMPLETE",
    "inventory": "DRIVE_RECURSIVE_ZIP_INVENTORY",
    "zip_files_count": len(zips),
    "items": zips
}

queue_doc = {
    "milestone": "P4.91F COMPLETE",
    "queue": "DRIVE_RECURSIVE_ABSORPTION_QUEUE",
    "items_count": len(absorption_queue),
    "items": absorption_queue
}

OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
ZIP_OUT.write_text(json.dumps(zip_doc, indent=2, ensure_ascii=False), encoding="utf-8")
QUEUE_OUT.write_text(json.dumps(queue_doc, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.91F COMPLETE",
    "remote": remote,
    "items_total": len(items),
    "files_total": len(files),
    "folders_total": len(folders),
    "zip_files": len(zips),
    "folders_walked": len(folders_seen),
    "errors": len(errors),
    "delete": "FORBIDDEN",
    "next": "P4.91G DRIVE_ZIP_RECURSIVE_ABSORPTION"
}, indent=2, ensure_ascii=False))
