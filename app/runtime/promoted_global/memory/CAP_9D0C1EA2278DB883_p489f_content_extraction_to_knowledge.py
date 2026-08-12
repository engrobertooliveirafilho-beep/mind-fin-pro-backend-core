import json
import re
from pathlib import Path
from datetime import datetime, timezone

INPUT = Path("runtime/file_ingestion/readers/multi_extension_reader_report.json")
OUT1 = Path("runtime/knowledge_extraction/extracted_knowledge.json")
OUT2 = Path("runtime/knowledge_extraction/queue/knowledge_queue.json")

data = json.loads(INPUT.read_text(encoding="utf-8"))
files = data.get("files", [])

PATTERNS = {
    "CAPABILITY": [
        r"capability",
        r"feature",
        r"function",
        r"engine",
        r"module"
    ],
    "BUG_FIX": [
        r"bug",
        r"exception",
        r"error",
        r"traceback",
        r"fix"
    ],
    "DEPENDENCY": [
        r"import ",
        r"dependency",
        r"requirements",
        r"package"
    ],
    "ARCHITECTURE": [
        r"architecture",
        r"pipeline",
        r"workflow",
        r"retrieval",
        r"memory"
    ],
    "UNIMPLEMENTED_IDEA": [
        r"todo",
        r"future",
        r"not implemented",
        r"pending",
        r"improvement"
    ]
}

knowledge = []
summary = {}

for item in files:

    if item.get("read_status") != "READ_OK":
        continue

    txt = (item.get("text_sample") or "").lower()

    for kind, rules in PATTERNS.items():

        hits = 0

        for rule in rules:
            hits += len(re.findall(rule, txt, re.I))

        if hits > 0:

            knowledge.append({
                "type": kind,
                "score": hits,
                "path": item["path"],
                "reader": item["reader"]
            })

            summary[kind] = summary.get(kind, 0) + hits

queue = sorted(
    knowledge,
    key=lambda x: x["score"],
    reverse=True
)

report = {
    "milestone": "P4.89F COMPLETE",
    "engine": "CONTENT_EXTRACTION_TO_KNOWLEDGE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "READ_ONLY_EXTRACTION",
    "physical_move": "NOT_EXECUTED",
    "delete": "FORBIDDEN",
    "knowledge_items": len(knowledge),
    "summary": summary,
    "next": "P4.89G UNKNOWN_EXTENSION_CLASSIFIER"
}

OUT1.write_text(
    json.dumps({
        "report": report,
        "knowledge": knowledge
    }, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

OUT2.write_text(
    json.dumps(queue, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps({
    "status": "P4.89F COMPLETE",
    "knowledge_items": len(knowledge),
    "summary": summary,
    "mode": "READ_ONLY_EXTRACTION",
    "next": "P4.89G UNKNOWN_EXTENSION_CLASSIFIER"
}, indent=2, ensure_ascii=False))
