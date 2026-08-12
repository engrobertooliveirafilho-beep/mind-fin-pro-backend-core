import json
from pathlib import Path
from datetime import datetime, timezone

INPUT = Path("runtime/file_ingestion/specialized_parsers/specialized_parser_backlog.json")

OUT1 = Path("runtime/parser_planning/specialized_parser_implementation_plan.json")
OUT2 = Path("runtime/parser_planning/parser_priority_queue.json")

data = json.loads(INPUT.read_text(encoding="utf-8"))

summary = data.get("parser_summary", {})

PARSER_CATALOG = {
    "generic_code_parser": {
        "priority": "P0",
        "purpose": "Ler código sem extensão conhecida",
        "risk": "LOW",
        "implementation_mode": "READ_ONLY"
    },
    "python_code_parser": {
        "priority": "P0",
        "purpose": "Ler artefatos Python",
        "risk": "LOW",
        "implementation_mode": "READ_ONLY"
    },
    "json_artifact_parser": {
        "priority": "P0",
        "purpose": "Ler artefatos estruturados",
        "risk": "LOW",
        "implementation_mode": "READ_ONLY"
    },
    "plain_text_fallback_reader": {
        "priority": "P1",
        "purpose": "Fallback universal",
        "risk": "LOW",
        "implementation_mode": "READ_ONLY"
    },
    "clean_trash_classifier": {
        "priority": "P2",
        "purpose": "Classificar lixo/cache",
        "risk": "LOW",
        "implementation_mode": "CLASSIFICATION_ONLY"
    },
    "manual_review": {
        "priority": "P3",
        "purpose": "Revisão humana",
        "risk": "NONE",
        "implementation_mode": "MANUAL"
    }
}

plan = []
queue = []

for parser_name, count in summary.items():

    meta = PARSER_CATALOG.get(
        parser_name,
        {
            "priority": "P9",
            "purpose": "UNKNOWN",
            "risk": "UNKNOWN",
            "implementation_mode": "MANUAL"
        }
    )

    item = {
        "parser": parser_name,
        "affected_files": count,
        "priority": meta["priority"],
        "purpose": meta["purpose"],
        "risk": meta["risk"],
        "implementation_mode": meta["implementation_mode"],
        "approval_required": True,
        "physical_move": "FORBIDDEN",
        "delete": "FORBIDDEN"
    }

    plan.append(item)
    queue.append(item)

priority_order = {
    "P0": 0,
    "P1": 1,
    "P2": 2,
    "P3": 3,
    "P9": 9
}

queue = sorted(
    queue,
    key=lambda x: (
        priority_order.get(x["priority"], 99),
        -x["affected_files"]
    )
)

implementation_plan = {
    "milestone": "P4.89I COMPLETE",
    "engine": "SPECIALIZED_PARSER_IMPLEMENTATION_PLAN",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "PLAN_ONLY",
    "approval_required": True,
    "physical_move": "FORBIDDEN",
    "delete": "FORBIDDEN",
    "parsers": plan,
    "next": "P4.89J FILE_INTELLIGENCE_EXPANSION_PLAN"
}

priority_queue = {
    "milestone": "P4.89I COMPLETE",
    "queue_type": "PARSER_PRIORITY_QUEUE",
    "items_count": len(queue),
    "items": queue
}

OUT1.write_text(
    json.dumps(implementation_plan, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

OUT2.write_text(
    json.dumps(priority_queue, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps({
    "status": "P4.89I COMPLETE",
    "parsers": len(plan),
    "highest_priority": [
        x["parser"]
        for x in queue
        if x["priority"] == "P0"
    ],
    "mode": "PLAN_ONLY",
    "next": "P4.89J FILE_INTELLIGENCE_EXPANSION_PLAN"
}, indent=2, ensure_ascii=False))
