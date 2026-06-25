import json
from pathlib import Path
from datetime import datetime, timezone

from app.runtime.drive_processed_queue import process_file

SUPPORTED = {
    ".txt", ".md", ".json", ".csv", ".log", ".py", ".ps1", ".yml", ".yaml"
}

def process_folder(folder: str, recursive: bool = True) -> dict:
    root = Path(folder)

    report = {
        "engine": "P4.78_BATCH_DRIVE_FOLDER_PROCESSOR",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "folder": str(root),
        "recursive": recursive,
        "total_seen": 0,
        "processed": 0,
        "skipped": 0,
        "errors": [],
        "items": [],
    }

    if not root.exists():
        report["errors"].append({"folder": str(root), "error": "folder_not_found"})
        return report

    files = root.rglob("*") if recursive else root.glob("*")

    for p in files:
        if not p.is_file():
            continue

        report["total_seen"] += 1

        if p.suffix.lower() not in SUPPORTED:
            report["skipped"] += 1
            report["items"].append({
                "file": str(p),
                "status": "skipped_unsupported_extension",
                "extension": p.suffix.lower()
            })
            continue

        try:
            out = process_file(str(p), move=True)
            if out.get("status") == "processed":
                report["processed"] += 1
            else:
                report["skipped"] += 1
            report["items"].append(out)
        except Exception as e:
            report["errors"].append({
                "file": str(p),
                "error": type(e).__name__ + ": " + str(e)[:500]
            })

    return report
