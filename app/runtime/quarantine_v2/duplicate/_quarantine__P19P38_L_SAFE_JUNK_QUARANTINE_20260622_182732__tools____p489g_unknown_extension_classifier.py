import json
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

INPUT = Path("runtime/file_ingestion/readers/multi_extension_reader_report.json")
OUT1 = Path("runtime/file_ingestion/unknown_extensions/unknown_extension_classification_report.json")
OUT2 = Path("runtime/file_ingestion/unknown_extensions/parser_backlog.json")

data = json.loads(INPUT.read_text(encoding="utf-8"))
files = data.get("files", [])

unknown = [f for f in files if f.get("read_status") == "UNKNOWN_EXTENSION"]

MEDIA_EXT = {".mp4",".mov",".avi",".mkv",".mp3",".wav",".m4a",".aac"}
BINARY_EXT = {".exe",".dll",".bin",".dat",".db",".sqlite",".pkl",".onnx"}
DOC_LIKE_EXT = {".rtf",".odt",".ods",".odp",".pages",".numbers",".key"}
CODE_LIKE_EXT = {".js",".ts",".tsx",".jsx",".css",".scss",".java",".cs",".cpp",".c",".h",".go",".rs",".php",".rb"}
TRASH_EXT = {".lock",".pid",".tmp",".temp",".old",".orig"}
NO_EXT_HINTS = {"dockerfile","makefile","license","readme"}

def classify(item):
    path = str(item.get("path",""))
    suffix = str(item.get("suffix","")).lower()
    name = Path(path).name.lower()

    if suffix in MEDIA_EXT:
        return "MEDIA_METADATA_ONLY"

    if suffix in BINARY_EXT:
        return "BINARY_REVIEW"

    if suffix in DOC_LIKE_EXT:
        return "DOCUMENT_PARSER_REQUIRED"

    if suffix in CODE_LIKE_EXT:
        return "TEXT_CODE_PARSER_REQUIRED"

    if suffix in TRASH_EXT:
        return "CLEAN_TRASH_CANDIDATE"

    if suffix == "" and any(h in name for h in NO_EXT_HINTS):
        return "TEXT_NO_EXTENSION_READER_REQUIRED"

    if suffix == "":
        return "NO_EXTENSION_REVIEW"

    return "UNKNOWN_REVIEW"

classified = []

for item in unknown:
    bucket = classify(item)
    classified.append({
        "path": item.get("path"),
        "suffix": item.get("suffix"),
        "size": item.get("size"),
        "classification": bucket,
        "physical_move": "NOT_EXECUTED",
        "delete": "FORBIDDEN",
        "approval_required": True
    })

summary = Counter(x["classification"] for x in classified)
suffix_summary = Counter((x.get("suffix") or "NO_EXT") for x in classified)

parser_backlog = [
    x for x in classified
    if x["classification"] in [
        "DOCUMENT_PARSER_REQUIRED",
        "TEXT_CODE_PARSER_REQUIRED",
        "TEXT_NO_EXTENSION_READER_REQUIRED",
        "NO_EXTENSION_REVIEW",
        "UNKNOWN_REVIEW"
    ]
]

report = {
    "milestone": "P4.89G COMPLETE",
    "engine": "UNKNOWN_EXTENSION_CLASSIFIER",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "CLASSIFY_ONLY",
    "physical_move": "NOT_EXECUTED",
    "delete": "FORBIDDEN",
    "unknown_total": len(unknown),
    "summary": dict(summary),
    "suffix_summary": dict(suffix_summary),
    "classified": classified,
    "next": "P4.89H SPECIALIZED_PARSER_BACKLOG"
}

backlog = {
    "milestone": "P4.89G COMPLETE",
    "backlog": "PARSER_BACKLOG",
    "mode": "PLAN_ONLY",
    "approval_required": True,
    "items_count": len(parser_backlog),
    "items": parser_backlog
}

OUT1.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
OUT2.write_text(json.dumps(backlog, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.89G COMPLETE",
    "unknown_total": len(unknown),
    "summary": dict(summary),
    "parser_backlog": len(parser_backlog),
    "mode": "CLASSIFY_ONLY",
    "next": "P4.89H SPECIALIZED_PARSER_BACKLOG"
}, indent=2, ensure_ascii=False))
