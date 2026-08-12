import json
from pathlib import Path
from datetime import datetime, timezone

REGISTRY = Path("app/runtime/universal_capability_registry.json")
EFFECTIVENESS = Path("runtime/capability_usage_ledger.jsonl")

KNOWN = {
    "semantic_retrieval": {"status": "ACTIVE", "domain": "retrieval"},
    "social_memory": {"status": "ACTIVE", "domain": "memory"},
    "emotional_report": {"status": "ACTIVE", "domain": "emotion"},
    "relational_report": {"status": "ACTIVE", "domain": "relationship"},
    "semantic_route": {"status": "READY", "domain": "routing"},
    "humanized_answer": {"status": "READY", "domain": "response"},
    "whatsapp_ux_guard": {"status": "READY", "domain": "whatsapp"},
    "relationalize": {"status": "READY", "domain": "relationship"},
    "persistent_cognitive_graph": {"status": "OPTIONAL", "domain": "knowledge_graph"},
    "eldora_semantic": {"status": "OPTIONAL", "domain": "semantic_api"},
}

def load_usage():
    usage = {}

    if not EFFECTIVENESS.exists():
        return usage

    for line in EFFECTIVENESS.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue

        cap = row.get("capability")
        if not cap:
            continue

        usage.setdefault(cap, {"usage": 0, "success": 0, "failed": 0})
        usage[cap]["usage"] += 1

        if row.get("success"):
            usage[cap]["success"] += 1
        else:
            usage[cap]["failed"] += 1

    return usage

def build_registry():
    usage = load_usage()

    registry = {
        "registry": "P4.75_UNIVERSAL_CAPABILITY_REGISTRY",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "capabilities": {},
        "summary": {}
    }

    for cap, meta in KNOWN.items():
        u = usage.get(cap, {"usage": 0, "success": 0, "failed": 0})
        total = u["usage"]
        success_rate = (u["success"] / total) if total else 0

        registry["capabilities"][cap] = {
            "status": meta["status"],
            "domain": meta["domain"],
            "usage": total,
            "success": u["success"],
            "failed": u["failed"],
            "success_rate": round(success_rate, 4),
            "eligible_for_runtime": meta["status"] in ["ACTIVE", "READY"],
        }

    counts = {}
    for c in registry["capabilities"].values():
        counts[c["status"]] = counts.get(c["status"], 0) + 1

    registry["summary"] = counts

    REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    return registry

if __name__ == "__main__":
    print(json.dumps(build_registry(), indent=2, ensure_ascii=False))
