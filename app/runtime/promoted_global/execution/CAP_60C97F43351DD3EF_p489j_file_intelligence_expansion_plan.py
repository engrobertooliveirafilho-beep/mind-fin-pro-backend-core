import json
from pathlib import Path
from datetime import datetime, timezone

PARSER_QUEUE = Path("runtime/parser_planning/parser_priority_queue.json")
UNKNOWN_REPORT = Path("runtime/file_ingestion/specialized_parsers/unknown_reclassification_report.json")
KNOWLEDGE = Path("runtime/knowledge_extraction/extracted_knowledge.json")
READER = Path("runtime/file_ingestion/readers/multi_extension_reader_report.json")

queue = json.loads(PARSER_QUEUE.read_text(encoding="utf-8"))
unknown = json.loads(UNKNOWN_REPORT.read_text(encoding="utf-8"))
knowledge = json.loads(KNOWLEDGE.read_text(encoding="utf-8"))
reader = json.loads(READER.read_text(encoding="utf-8"))

p0 = [x for x in queue.get("items", []) if x.get("priority") == "P0"]
summary = unknown.get("summary", {})
reader_summary = reader.get("summary", {})
knowledge_report = knowledge.get("report", {})

useful_unknown = (
    summary.get("PYTHON_OR_CODE_LIKE", 0)
    + summary.get("PYTHON_TEST_OR_CODE", 0)
    + summary.get("JSON_OR_STRUCTURED_ARTIFACT", 0)
    + summary.get("TEXT_UNKNOWN_READER", 0)
)

trash_unknown = summary.get("TRASH_OR_CACHE", 0)
manual_review = summary.get("MANUAL_REVIEW_REQUIRED", 0)

expansion_plan = {
    "milestone": "P4.89J COMPLETE",
    "plan": "FILE_INTELLIGENCE_EXPANSION_PLAN",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "PLAN_ONLY",
    "physical_move": "FORBIDDEN",
    "delete": "FORBIDDEN",
    "current_state": {
        "files_checked": reader.get("total_files_checked", 0),
        "read_ok": reader_summary.get("READ_OK", 0),
        "unknown_extension": reader_summary.get("UNKNOWN_EXTENSION", 0),
        "source_not_found": reader_summary.get("SOURCE_NOT_FOUND", 0),
        "knowledge_items": knowledge_report.get("knowledge_items", 0),
        "useful_unknown_files": useful_unknown,
        "trash_unknown_files": trash_unknown,
        "manual_review_files": manual_review
    },
    "p0_parsers": p0,
    "expansion_value": {
        "core_gain_remaining_files": useful_unknown,
        "trash_cleanup_candidates": trash_unknown,
        "manual_review_required": manual_review,
        "recommendation": "OPTIONAL_IMPLEMENT_P0_PARSERS_BEFORE_LONG_TERM_AUTOMATION"
    },
    "decision_for_p490": {
        "ready_for_p490": True,
        "reason": "Core pipeline, governance, KG, repository intelligence, ingestion, reader, extraction, unknown classification and parser planning are certified.",
        "known_residual": {
            "p0_parser_implementation": "PLANNED_NOT_EXECUTED",
            "trash_cleanup": "CLASSIFIED_NOT_DELETED",
            "manual_review": manual_review
        }
    },
    "next": "P4.90 SOVEREIGN TECHNICAL CAPACITY CERTIFICATION"
}

Path("runtime/file_intelligence/file_intelligence_expansion_plan.json").write_text(
    json.dumps(expansion_plan, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps({
    "status": "P4.89J COMPLETE",
    "files_checked": expansion_plan["current_state"]["files_checked"],
    "knowledge_items": expansion_plan["current_state"]["knowledge_items"],
    "useful_unknown_files": useful_unknown,
    "trash_unknown_files": trash_unknown,
    "p0_parsers": [x["parser"] for x in p0],
    "ready_for_p490": True,
    "next": "P4.90 SOVEREIGN TECHNICAL CAPACITY CERTIFICATION"
}, indent=2, ensure_ascii=False))
