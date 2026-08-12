import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

from app.runtime.drive_batch_processor import process_folder
from app.runtime.knowledge_extraction_engine import extract_items
from app.runtime.capability_reconstruction_planner import plan_from_extraction

SUPPORTED = {".txt", ".md", ".json", ".csv", ".log", ".py", ".ps1", ".yml", ".yaml"}

def run_deep_absorption(folder: str, recursive: bool = True) -> dict:
    root = Path(folder)

    result = {
        "engine": "P4.78_80_FULL_DRIVE_DEEP_ABSORPTION",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "folder": str(root),
        "batch": None,
        "extractions": [],
        "plans": [],
        "summary": {
            "files_seen": 0,
            "files_extracted": 0,
            "missions_created": 0
        }
    }

    batch = process_folder(str(root), recursive=recursive)
    result["batch"] = batch
    result["summary"]["files_seen"] = batch.get("total_seen", 0)

    files = root.rglob("*") if recursive else root.glob("*")

    for p in files:
        if not p.is_file() or p.suffix.lower() not in SUPPORTED:
            continue

        text = p.read_text(encoding="utf-8", errors="ignore")
        source_id = str(p).replace("\\", "/")

        extraction = extract_items(
            source_id=source_id,
            text=text,
            metadata={"file": str(p)}
        )

        if extraction.get("total_items", 0) > 0:
            result["summary"]["files_extracted"] += 1

        plan = plan_from_extraction(extraction)

        result["extractions"].append({
            "file": str(p),
            "items": extraction.get("total_items", 0),
            "summary": extraction.get("summary", {})
        })

        result["plans"].append({
            "file": str(p),
            "missions": plan.get("total_missions", 0),
            "summary": plan.get("summary", {})
        })

        result["summary"]["missions_created"] += plan.get("total_missions", 0)

    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True)
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    out = run_deep_absorption(args.folder, recursive=not args.no_recursive)
    text = json.dumps(out, indent=2, ensure_ascii=False, default=str)
    print(text)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")

if __name__ == "__main__":
    main()
