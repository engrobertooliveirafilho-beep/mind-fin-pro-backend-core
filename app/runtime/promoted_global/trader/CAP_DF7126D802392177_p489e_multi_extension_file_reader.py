import json
import csv
from pathlib import Path
from datetime import datetime, timezone

MANIFEST = Path("runtime/file_ingestion/input_manifest.json")
OUT = Path("runtime/file_ingestion/readers/multi_extension_reader_report.json")

TEXT_EXT = {".py",".json",".txt",".md",".csv",".log",".yml",".yaml",".toml",".html",".xml",".sql",".ps1",".bat",".env"}
SPECIAL_EXT = {".docx",".xlsx",".pptx",".pdf"}
IMAGE_EXT = {".png",".jpg",".jpeg",".webp",".gif",".bmp"}
ARCHIVE_EXT = {".zip",".rar",".7z",".tar",".gz"}

def read_sample(path, suffix, limit=4000):
    p = Path(path)

    if suffix in TEXT_EXT:
        try:
            return {
                "read_status": "READ_OK",
                "reader": "text_reader",
                "text_sample": p.read_text(encoding="utf-8", errors="ignore")[:limit],
                "metadata_only": False
            }
        except Exception as e:
            return {
                "read_status": "READ_ERROR",
                "reader": "text_reader",
                "error": repr(e),
                "text_sample": "",
                "metadata_only": False
            }

    if suffix in SPECIAL_EXT:
        return {
            "read_status": "REVIEW_REQUIRED",
            "reader": "specialized_parser_required",
            "text_sample": "",
            "metadata_only": True
        }

    if suffix in IMAGE_EXT:
        return {
            "read_status": "METADATA_ONLY",
            "reader": "image_metadata_reader",
            "text_sample": "",
            "metadata_only": True
        }

    if suffix in ARCHIVE_EXT:
        return {
            "read_status": "ARCHIVE_CONTAINER",
            "reader": "archive_metadata_reader",
            "text_sample": "",
            "metadata_only": True
        }

    return {
        "read_status": "UNKNOWN_EXTENSION",
        "reader": "metadata_only_reader",
        "text_sample": "",
        "metadata_only": True
    }

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
files = []

for q, items in manifest.get("queues", {}).items():
    for item in items:
        path = item.get("path")
        suffix = (item.get("suffix") or Path(path).suffix).lower()
        exists = Path(path).exists()

        record = {
            "path": path,
            "queue": q,
            "suffix": suffix,
            "exists": exists,
            "size": item.get("size"),
        }

        if exists:
            record.update(read_sample(path, suffix))
        else:
            record.update({
                "read_status": "SOURCE_NOT_FOUND",
                "reader": "none",
                "text_sample": "",
                "metadata_only": True
            })

        files.append(record)

summary = {}
for f in files:
    key = f["read_status"]
    summary[key] = summary.get(key, 0) + 1

report = {
    "milestone": "P4.89E COMPLETE",
    "reader": "MULTI_EXTENSION_FILE_READER",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "SAFE_READ_AND_METADATA_ONLY",
    "physical_move": "NOT_EXECUTED",
    "delete": "FORBIDDEN",
    "supported_text_extensions": sorted(TEXT_EXT),
    "specialized_parser_extensions": sorted(SPECIAL_EXT),
    "image_extensions_metadata_only": sorted(IMAGE_EXT),
    "archive_extensions_metadata_only": sorted(ARCHIVE_EXT),
    "total_files_checked": len(files),
    "summary": summary,
    "files": files,
    "next": "P4.89F CONTENT EXTRACTION TO KNOWLEDGE"
}

OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.89E COMPLETE",
    "total_files_checked": len(files),
    "summary": summary,
    "mode": "SAFE_READ_AND_METADATA_ONLY",
    "next": "P4.89F CONTENT EXTRACTION TO KNOWLEDGE"
}, indent=2, ensure_ascii=False))
