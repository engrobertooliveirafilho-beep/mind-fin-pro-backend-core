import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

from app.runtime.drive_capability_absorption import absorb_text_source

ROOT = Path("runtime/drive_queue")
PENDING = ROOT / "pending"
PROCESSED = ROOT / "processed"
REVIEW = ROOT / "review"
ARCHIVE = ROOT / "archive"
LEDGER = ROOT / "processed_ledger.jsonl"

for p in [PENDING, PROCESSED, REVIEW, ARCHIVE]:
    p.mkdir(parents=True, exist_ok=True)

def _safe_name(path: Path) -> str:
    return path.name.replace("/", "_").replace("\\", "_").replace(":", "_")

def already_processed(file_path: str) -> bool:
    p = Path(file_path)
    if not LEDGER.exists():
        return False

    key = str(p.resolve()).lower()

    for line in LEDGER.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if str(row.get("source_path", "")).lower() == key:
            return True

    return False

def mark_processed(source_path: str, result: dict, destination: str):
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_path": str(Path(source_path).resolve()),
        "destination": destination,
        "matched": result.get("matched"),
        "recommended_action": result.get("recommended_action"),
        "matches": result.get("matches", []),
    }

    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return row

def process_file(file_path: str, move: bool = True) -> dict:
    p = Path(file_path)

    if not p.exists():
        return {
            "status": "missing",
            "file": str(p),
        }

    if already_processed(str(p)):
        return {
            "status": "already_processed",
            "file": str(p),
        }

    text = p.read_text(encoding="utf-8", errors="ignore")

    result = absorb_text_source(
        source_id=_safe_name(p),
        text=text,
        metadata={"file": str(p)}
    )

    action = result.get("recommended_action")

    if action == "QUEUE_FOR_RUNTIME_REVIEW":
        dest_dir = REVIEW
    elif action == "QUEUE_FOR_ADAPTER_REVIEW":
        dest_dir = REVIEW
    else:
        dest_dir = ARCHIVE

    dest = dest_dir / _safe_name(p)

    if move:
        shutil.copy2(p, dest)
        processed_copy = PROCESSED / _safe_name(p)
        shutil.copy2(p, processed_copy)

    row = mark_processed(str(p), result, str(dest))

    return {
        "status": "processed",
        "file": str(p),
        "destination": str(dest),
        "ledger": row,
        "absorption": result,
    }
