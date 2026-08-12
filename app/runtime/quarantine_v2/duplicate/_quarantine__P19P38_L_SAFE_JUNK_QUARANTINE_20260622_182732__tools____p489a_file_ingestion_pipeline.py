import json
from pathlib import Path
from datetime import datetime, timezone

ROOTS = ["app", "runtime", "tools", "tests", "_evidence", "_maintenance"]
OUT = Path("runtime/file_ingestion")

TRASH_PATTERNS = [
    "__pycache__",
    ".pytest_cache",
    ".DS_Store",
    "Thumbs.db",
    ".tmp",
    ".bak",
    ".log",
    ".cache",
    "node_modules",
    ".venv",
    "venv"
]

REVIEW_PATTERNS = [
    "broken",
    "candidate",
    "backup",
    "before",
    "after",
    "patch",
    "rollback"
]

PROCESS_EXT = [".py", ".json", ".md", ".txt", ".yml", ".yaml", ".toml"]

def classify(path):
    p = str(path).lower()
    suffix = Path(path).suffix.lower()

    if any(x.lower() in p for x in TRASH_PATTERNS):
        return "CLEAN_TRASH"

    if any(x.lower() in p for x in REVIEW_PATTERNS):
        return "REVIEW"

    if suffix in PROCESS_EXT:
        return "PROCESS"

    return "ARCHIVE"

def safe_read_sample(path, limit=2000):
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""

files = []

for root in ROOTS:
    r = Path(root)
    if not r.exists():
        continue

    for f in r.rglob("*"):
        if f.is_file():
            q = classify(f)
            files.append({
                "path": str(f.as_posix()),
                "suffix": f.suffix.lower(),
                "size": f.stat().st_size,
                "queue": q,
                "movement_status": "BLOCKED_BY_P4.83_GATE",
                "knowledge_sample": safe_read_sample(f) if q in ["PROCESS", "REVIEW"] else "",
                "trash_reason": "Detected as cache/temp/low-value artifact" if q == "CLEAN_TRASH" else None
            })

queues = {
    "PROCESS": [x for x in files if x["queue"] == "PROCESS"],
    "REVIEW": [x for x in files if x["queue"] == "REVIEW"],
    "ARCHIVE": [x for x in files if x["queue"] == "ARCHIVE"],
    "CLEAN_TRASH": [x for x in files if x["queue"] == "CLEAN_TRASH"],
}

manifest = {
    "milestone": "P4.89A COMPLETE",
    "pipeline": "FILE_INGESTION_AND_PROCESSING_PIPELINE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "SCAN_AND_CLASSIFY_ONLY",
    "physical_move": "FORBIDDEN_WITHOUT_APPROVAL",
    "governance": "P4.83_ENFORCED",
    "roots_scanned": ROOTS,
    "total_files": len(files),
    "queues_count": {k: len(v) for k, v in queues.items()},
    "queues": queues,
    "next": "P4.89B SAFE PHYSICAL FILE ROUTING"
}

trash_knowledge = {
    "milestone": "P4.89A COMPLETE",
    "clean_trash_mode": "ACTIVE",
    "purpose": "Registrar lixo/sujeira como conhecimento operacional antes de qualquer limpeza física.",
    "physical_delete": "FORBIDDEN",
    "physical_move": "FORBIDDEN_WITHOUT_APPROVAL",
    "total_trash_candidates": len(queues["CLEAN_TRASH"]),
    "trash_candidates": queues["CLEAN_TRASH"]
}

(OUT / "input_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "processing_ledger.json").write_text(json.dumps(files, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "queues" / "process_files.json").write_text(json.dumps(queues["PROCESS"], indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "queues" / "review_files.json").write_text(json.dumps(queues["REVIEW"], indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "queues" / "archive_files.json").write_text(json.dumps(queues["ARCHIVE"], indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "clean_trash" / "clean_trash_knowledge.json").write_text(json.dumps(trash_knowledge, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.89A COMPLETE",
    "total_files": len(files),
    "process": len(queues["PROCESS"]),
    "review": len(queues["REVIEW"]),
    "archive": len(queues["ARCHIVE"]),
    "clean_trash": len(queues["CLEAN_TRASH"]),
    "mode": "SCAN_AND_CLASSIFY_ONLY",
    "physical_move": "FORBIDDEN_WITHOUT_APPROVAL",
    "next": "P4.89B SAFE PHYSICAL FILE ROUTING"
}, indent=2, ensure_ascii=False))
