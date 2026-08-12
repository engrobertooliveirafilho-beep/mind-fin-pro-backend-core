import json
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

INPUT = Path("runtime/file_ingestion/unknown_extensions/unknown_extension_classification_report.json")
OUT1 = Path("runtime/file_ingestion/specialized_parsers/specialized_parser_backlog.json")
OUT2 = Path("runtime/file_ingestion/specialized_parsers/unknown_reclassification_report.json")

data = json.loads(INPUT.read_text(encoding="utf-8"))
items = data.get("classified", [])

def sample(path, limit=2048):
    try:
        p = Path(path)
        if not p.exists():
            return ""
        return p.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""

def classify(item):
    path = str(item.get("path") or "")
    suffix = str(item.get("suffix") or "").lower()
    name = Path(path).name.lower()
    low_path = path.lower()
    text = sample(path).lower()

    combined = " ".join([name, low_path, text])

    if any(x in combined for x in ["__pycache__", ".pytest_cache", "cache", "tmp", "temp", ".bak", ".old"]):
        return "TRASH_OR_CACHE"

    if any(x in combined for x in ["pytest", "assert ", "def test_", "unittest"]):
        return "PYTHON_TEST_OR_CODE"

    if any(x in combined for x in ["def ", "class ", "import ", "from "]):
        return "PYTHON_OR_CODE_LIKE"

    if any(x in combined for x in ["{", "}", '"status"', '"milestone"', '"error"', '"summary"']):
        return "JSON_OR_STRUCTURED_ARTIFACT"

    if any(x in combined for x in ["powershell", "param(", "write-host", "$erroractionpreference"]):
        return "POWERSHELL_OR_SCRIPT"

    if any(x in combined for x in ["select ", "insert ", "update ", "create table", "alter table"]):
        return "SQL_OR_SCHEMA"

    if any(x in combined for x in ["markdown", "# ", "## ", "objetivo", "diagnóstico", "diagnostico"]):
        return "MARKDOWN_OR_TEXT_DOC"

    if any(x in combined for x in ["traceback", "exception", "failed", "error collecting"]):
        return "LOG_OR_ERROR_EVIDENCE"

    if any(x in combined for x in ["png", "jpg", "jpeg", "webp", "image"]):
        return "IMAGE_OR_MEDIA_METADATA"

    if any(x in combined for x in ["pdf", "docx", "xlsx", "pptx"]):
        return "DOCUMENT_SPECIAL_PARSER"

    if len(text.strip()) > 0:
        return "TEXT_UNKNOWN_READER"

    return "MANUAL_REVIEW_REQUIRED"

reclassified = []

for item in items:
    bucket = classify(item)
    parser = {
        "PYTHON_TEST_OR_CODE": "python_code_parser",
        "PYTHON_OR_CODE_LIKE": "generic_code_parser",
        "JSON_OR_STRUCTURED_ARTIFACT": "json_artifact_parser",
        "POWERSHELL_OR_SCRIPT": "powershell_script_parser",
        "SQL_OR_SCHEMA": "sql_schema_parser",
        "MARKDOWN_OR_TEXT_DOC": "markdown_text_parser",
        "LOG_OR_ERROR_EVIDENCE": "log_error_parser",
        "IMAGE_OR_MEDIA_METADATA": "image_metadata_parser",
        "DOCUMENT_SPECIAL_PARSER": "document_parser",
        "TEXT_UNKNOWN_READER": "plain_text_fallback_reader",
        "TRASH_OR_CACHE": "clean_trash_classifier",
        "MANUAL_REVIEW_REQUIRED": "manual_review"
    }.get(bucket, "manual_review")

    reclassified.append({
        **item,
        "reclassified_as": bucket,
        "recommended_parser": parser,
        "physical_move": "NOT_EXECUTED",
        "delete": "FORBIDDEN",
        "approval_required": True
    })

summary = Counter(x["reclassified_as"] for x in reclassified)
parser_summary = Counter(x["recommended_parser"] for x in reclassified)

backlog = {
    "milestone": "P4.89H COMPLETE",
    "backlog": "SPECIALIZED_PARSER_BACKLOG",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "PLAN_ONLY",
    "physical_move": "NOT_EXECUTED",
    "delete": "FORBIDDEN",
    "items_count": len(reclassified),
    "parser_summary": dict(parser_summary),
    "items": reclassified,
    "next": "P4.89I SPECIALIZED PARSER IMPLEMENTATION PLAN"
}

report = {
    "milestone": "P4.89H COMPLETE",
    "engine": "UNKNOWN_RECLASSIFICATION_ENGINE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "CLASSIFY_ONLY",
    "unknown_input": len(items),
    "summary": dict(summary),
    "parser_summary": dict(parser_summary),
    "next": "P4.89I SPECIALIZED PARSER IMPLEMENTATION PLAN"
}

OUT1.write_text(json.dumps(backlog, indent=2, ensure_ascii=False), encoding="utf-8")
OUT2.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.89H COMPLETE",
    "unknown_input": len(items),
    "summary": dict(summary),
    "parser_summary": dict(parser_summary),
    "mode": "CLASSIFY_ONLY",
    "next": "P4.89I SPECIALIZED PARSER IMPLEMENTATION PLAN"
}, indent=2, ensure_ascii=False))
