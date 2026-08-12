import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOTS = ["app", "runtime", "tools", "tests", "_evidence", "_backup", "backups", "_maintenance"]
OUT_INDEX = Path("runtime/archive_ingestion/zip_index/zip_archive_index.json")
OUT_EXTRACT = Path("runtime/archive_ingestion/zip_extraction_ledger.json")
EXTRACT_ROOT = Path("runtime/archive_ingestion/extracted_safe")

MAX_EXTRACT_PER_ZIP = 50
MAX_FILE_SIZE = 5_000_000
SAFE_EXT = {".py",".json",".txt",".md",".csv",".log",".yml",".yaml",".toml",".html",".xml",".sql",".ps1",".bat",".env"}

zip_files = []
for root in ROOTS:
    r = Path(root)
    if r.exists():
        zip_files.extend([p for p in r.rglob("*.zip") if p.is_file()])

archives = []
extracted = []
skipped = []
errors = []

def safe_name(s):
    return hashlib.sha256(str(s).encode("utf-8")).hexdigest()[:20]

for zpath in zip_files:
    archive_id = safe_name(zpath.as_posix())
    entry_rows = []

    try:
        with zipfile.ZipFile(zpath, "r") as z:
            infos = z.infolist()

            for info in infos:
                entry_path = info.filename
                suffix = Path(entry_path).suffix.lower()
                is_dir = info.is_dir()
                too_large = info.file_size > MAX_FILE_SIZE
                safe_ext = suffix in SAFE_EXT
                suspicious = (
                    ".." in Path(entry_path).parts
                    or entry_path.startswith("/")
                    or entry_path.startswith("\\")
                )

                classification = "EXTRACTABLE_TEXT" if (safe_ext and not is_dir and not too_large and not suspicious) else "INDEX_ONLY"

                entry_rows.append({
                    "archive": zpath.as_posix(),
                    "entry": entry_path,
                    "suffix": suffix,
                    "size": info.file_size,
                    "is_dir": is_dir,
                    "classification": classification,
                    "too_large": too_large,
                    "suspicious_path": suspicious
                })

            extract_count = 0
            for row in entry_rows:
                if row["classification"] != "EXTRACTABLE_TEXT":
                    skipped.append({**row, "reason": "NOT_EXTRACTABLE_TEXT"})
                    continue

                if extract_count >= MAX_EXTRACT_PER_ZIP:
                    skipped.append({**row, "reason": "ZIP_EXTRACT_LIMIT_REACHED"})
                    continue

                try:
                    target_dir = EXTRACT_ROOT / archive_id
                    target_dir.mkdir(parents=True, exist_ok=True)

                    entry_hash = safe_name(row["entry"])
                    target = target_dir / f"{entry_hash}{row['suffix']}"

                    if target.exists():
                        skipped.append({**row, "reason": "TARGET_EXISTS", "target": target.as_posix()})
                        continue

                    with z.open(row["entry"]) as src:
                        data = src.read(MAX_FILE_SIZE + 1)

                    if len(data) > MAX_FILE_SIZE:
                        skipped.append({**row, "reason": "EXTRACTED_TOO_LARGE"})
                        continue

                    target.write_bytes(data)
                    extract_count += 1

                    extracted.append({
                        "archive": zpath.as_posix(),
                        "entry": row["entry"],
                        "target": target.as_posix(),
                        "suffix": row["suffix"],
                        "size": row["size"],
                        "delete_original_zip": False,
                        "physical_move_original_zip": "NOT_EXECUTED"
                    })

                except Exception as e:
                    errors.append({**row, "error": repr(e)})

        archives.append({
            "archive": zpath.as_posix(),
            "archive_id": archive_id,
            "entries_count": len(entry_rows),
            "entries": entry_rows
        })

    except Exception as e:
        errors.append({
            "archive": zpath.as_posix(),
            "error": repr(e)
        })

index = {
    "milestone": "P4.91B COMPLETE",
    "engine": "ZIP_ARCHIVE_READER_AND_EXTRACTOR",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "SAFE_ZIP_INDEX_AND_LIMITED_EXTRACT",
    "delete_original_zip": "FORBIDDEN",
    "move_original_zip": "FORBIDDEN",
    "max_extract_per_zip": MAX_EXTRACT_PER_ZIP,
    "max_file_size": MAX_FILE_SIZE,
    "zip_files_found": len(zip_files),
    "archives_indexed": len(archives),
    "archives": archives,
    "next": "P4.91C EXTRACTED_ARCHIVE_CONTENT_READER"
}

ledger = {
    "milestone": "P4.91B COMPLETE",
    "extraction": "SAFE_LIMITED_ZIP_EXTRACTION",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "extracted_count": len(extracted),
    "skipped_count": len(skipped),
    "errors_count": len(errors),
    "extracted": extracted,
    "skipped": skipped,
    "errors": errors
}

OUT_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
OUT_EXTRACT.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.91B COMPLETE",
    "zip_files_found": len(zip_files),
    "archives_indexed": len(archives),
    "extracted": len(extracted),
    "skipped": len(skipped),
    "errors": len(errors),
    "delete_original_zip": "FORBIDDEN",
    "next": "P4.91C EXTRACTED_ARCHIVE_CONTENT_READER"
}, indent=2, ensure_ascii=False))
