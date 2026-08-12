import json, subprocess, time, sys
from pathlib import Path
from datetime import datetime, timezone
from collections import deque

DRIVE_FOLDER_ID = "1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"
OUT = Path("runtime/drive_absorption/monitor/drive_scan_monitor_report.json")
LOG = Path("runtime/drive_absorption/monitor/drive_scan_monitor.log")

MAX_FOLDERS = 500
MAX_DEPTH = 10
ARCHIVE_EXT = {".zip",".rar",".7z",".tar",".gz",".bz2"}

def safe_console(s):
    return str(s).encode("ascii", errors="replace").decode("ascii")

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    safe = safe_console(line)
    print(safe, flush=True)
    with LOG.open("a", encoding="utf-8", errors="replace") as f:
        f.write(line + "\n")

def run_cmd(cmd, timeout=45):
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"
    except Exception as e:
        return 999, "", repr(e)

def get_remote():
    rc, out, err = run_cmd(["rclone", "listremotes"], timeout=10)
    remotes = [x.strip().rstrip(":") for x in out.splitlines() if x.strip()]
    if "gdrive" in remotes:
        return "gdrive"
    return remotes[0] if remotes else None

LOG.write_text("", encoding="utf-8")

remote = get_remote()
folders_seen = set()
queue = deque()
errors = []
items = 0
files = 0
folders = 0
zips = 0

start = time.time()

if not remote:
    status = "NO_RCLONE_REMOTE"
    log("ERRO: nenhum remote rclone encontrado.")
else:
    status = "RUNNING"
    queue.append({"path": "", "depth": 0})
    log(f"INICIANDO VARREDURA DRIVE | remote={remote} | folder_id={DRIVE_FOLDER_ID}")

try:
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
            log(f"SKIP DEPTH MAX | {folder_path}")
            continue

        remote_path = f"{remote}:{folder_path}" if folder_path else f"{remote}:"

        log(f"SCAN FOLDER depth={depth} | {folder_path or '/'}")

        rc, stdout, stderr = run_cmd(
            ["rclone", "lsjson", remote_path, "--drive-root-folder-id", DRIVE_FOLDER_ID],
            timeout=45
        )

        if rc != 0:
            errors.append({"folder": folder_path, "returncode": rc, "error": stderr[:500]})
            log(f"ERRO FOLDER | {folder_path or '/'} | rc={rc} | {stderr[:120]}")
            continue

        try:
            data = json.loads(stdout)
        except Exception as e:
            errors.append({"folder": folder_path, "error": "JSON_PARSE_FAILED", "detail": repr(e)})
            log(f"ERRO JSON | {folder_path or '/'}")
            continue

        folder_files = 0
        folder_folders = 0
        folder_zips = 0

        for obj in data:
            name = obj.get("Name") or obj.get("Path") or ""
            rel = f"{folder_path}/{name}".strip("/") if folder_path else name
            is_dir = bool(obj.get("IsDir"))

            items += 1

            if is_dir:
                folders += 1
                folder_folders += 1
                queue.append({"path": rel, "depth": depth + 1})
            else:
                files += 1
                folder_files += 1

                if Path(rel).suffix.lower() in ARCHIVE_EXT:
                    zips += 1
                    folder_zips += 1
                    log(f"ZIP DETECTADO | {rel}")

        log(
            f"FOLDER OK | {folder_path or '/'} | files={folder_files} folders={folder_folders} zips={folder_zips} | total_files={files} total_zips={zips}"
        )

    status = "COMPLETE" if remote else status

except Exception as e:
    status = "FAILED_BUT_REPORTED"
    errors.append({"fatal_error": repr(e)})
    log(f"FATAL CAPTURADO | {repr(e)}")

report = {
    "milestone": "P4.91F3 COMPLETE",
    "monitor": "DRIVE_SCAN_MONITOR_ASCII_SAFE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "status": status,
    "remote": remote,
    "drive_folder_id": DRIVE_FOLDER_ID,
    "mode": "PRINT_SCAN_PROGRESS_ASCII_SAFE",
    "delete": "FORBIDDEN",
    "move_original": "FORBIDDEN",
    "folders_walked": len(folders_seen),
    "items_total": items,
    "files_total": files,
    "folders_total": folders,
    "zip_files": zips,
    "errors_count": len(errors),
    "elapsed_seconds": round(time.time() - start, 2),
    "errors": errors
}

OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

log(f"FINALIZADO | status={status} files={files} folders={folders} zips={zips} errors={len(errors)} elapsed={report['elapsed_seconds']}s")
print(json.dumps(report, indent=2, ensure_ascii=False))
