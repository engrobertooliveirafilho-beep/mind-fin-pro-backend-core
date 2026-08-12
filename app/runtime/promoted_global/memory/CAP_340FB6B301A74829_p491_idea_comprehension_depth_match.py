import json
from pathlib import Path
from datetime import datetime, timezone

KNOWLEDGE = Path("runtime/knowledge_extraction/extracted_knowledge.json")
KG = Path("runtime/knowledge_graph/drive_knowledge_graph.json")
REGISTRY = Path("app/runtime/universal_capability_registry.json")
REPO = Path("runtime/repository_intelligence/full_repository_intelligence_report.json")

OUT1 = Path("runtime/idea_intelligence/idea_comprehension_report.json")
OUT2 = Path("runtime/idea_intelligence/module_depth_match_report.json")
OUT3 = Path("runtime/idea_intelligence/idea_resolution_backlog.json")

def load(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": repr(e)}

knowledge = load(KNOWLEDGE)
kg = load(KG)
registry = load(REGISTRY)
repo = load(REPO)

items = knowledge.get("knowledge", [])
ideas = [x for x in items if x.get("type") in ["UNIMPLEMENTED_IDEA", "INCOMPLETE_FEATURE"]]

capability_text = json.dumps({
    "kg": kg,
    "registry": registry,
    "repo": repo
}, ensure_ascii=False).lower()

DOMAINS = {
    "memory": ["memory", "memória", "memoria", "context", "continuity"],
    "retrieval": ["retrieval", "embedding", "pgvector", "semantic"],
    "whatsapp_runtime": ["whatsapp", "reply", "conversation", "runtime"],
    "knowledge_extraction": ["knowledge", "extraction", "extract", "idea"],
    "file_ingestion": ["file", "ingestion", "reader", "extension"],
    "governance": ["governance", "approval", "gate", "lock"],
    "capability_recovery": ["capability", "orphan", "adapter", "recovery"],
    "repository_intelligence": ["repository", "intelligence", "architecture", "dependency"]
}

def detect_domain(text):
    low = text.lower()
    scores = {}
    for domain, terms in DOMAINS.items():
        scores[domain] = sum(1 for t in terms if t in low)
    best = max(scores.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else "unknown"

def depth_score(domain):
    terms = DOMAINS.get(domain, [])
    score = sum(capability_text.count(t.lower()) for t in terms)
    if score >= 20:
        return "DEEP_MODULE_AVAILABLE", min(100, score)
    if score >= 5:
        return "PARTIAL_MODULE_AVAILABLE", min(100, score)
    return "NO_DEEP_MODULE_FOUND", score

comprehended = []
backlog = []

for idx, idea in enumerate(ideas, start=1):
    raw = json.dumps(idea, ensure_ascii=False)
    domain = detect_domain(raw)
    depth_status, score = depth_score(domain)

    row = {
        "idea_id": f"IDEA-{idx:04d}",
        "source_path": idea.get("path"),
        "raw_type": idea.get("type"),
        "domain": domain,
        "comprehension": {
            "intent": "technical_improvement_or_unimplemented_capability",
            "expected_value": "UNKNOWN_UNTIL_REVIEW",
            "risk": "BLOCKED_BY_P4.83_GATE"
        },
        "module_depth_match": {
            "status": depth_status,
            "depth_score": score,
            "requires_new_module": depth_status == "NO_DEEP_MODULE_FOUND",
            "requires_adapter_or_extension": depth_status == "PARTIAL_MODULE_AVAILABLE",
            "can_attach_to_existing_module": depth_status == "DEEP_MODULE_AVAILABLE"
        },
        "execution": {
            "mode": "ANALYSIS_ONLY",
            "implementation": "FORBIDDEN",
            "approval_required": True
        }
    }

    comprehended.append(row)

    if depth_status != "DEEP_MODULE_AVAILABLE":
        backlog.append({
            "backlog_id": f"P4.91-B{len(backlog)+1:04d}",
            "idea_id": row["idea_id"],
            "domain": domain,
            "reason": depth_status,
            "recommended_action": "CREATE_ADAPTER_OR_MODULE_DEPTH_PLAN",
            "approval_status": "PENDING_APPROVAL",
            "execution_status": "BLOCKED_BY_P4.83_GATE"
        })

summary = {}
for row in comprehended:
    key = row["module_depth_match"]["status"]
    summary[key] = summary.get(key, 0) + 1

report = {
    "milestone": "P4.91 COMPLETE",
    "engine": "IDEA_COMPREHENSION_ENGINE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "ANALYSIS_ONLY",
    "ideas_detected": len(ideas),
    "ideas_comprehended": len(comprehended),
    "summary": summary,
    "items": comprehended,
    "next": "P4.92 IDEA_TO_CAPABILITY_PLANNING"
}

depth = {
    "milestone": "P4.91 COMPLETE",
    "engine": "MODULE_DEPTH_MATCH_ENGINE",
    "mode": "ANALYSIS_ONLY",
    "summary": summary,
    "domains": DOMAINS,
    "items": comprehended
}

resolution = {
    "milestone": "P4.91 COMPLETE",
    "backlog": "IDEA_RESOLUTION_BACKLOG",
    "mode": "PLAN_ONLY",
    "implementation": "FORBIDDEN",
    "approval_required": True,
    "items_count": len(backlog),
    "items": backlog
}

OUT1.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
OUT2.write_text(json.dumps(depth, indent=2, ensure_ascii=False), encoding="utf-8")
OUT3.write_text(json.dumps(resolution, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.91 COMPLETE",
    "ideas_detected": len(ideas),
    "ideas_comprehended": len(comprehended),
    "summary": summary,
    "backlog_items": len(backlog),
    "mode": "ANALYSIS_ONLY",
    "next": "P4.92 IDEA_TO_CAPABILITY_PLANNING"
}, indent=2, ensure_ascii=False))
