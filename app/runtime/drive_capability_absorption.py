import json
from pathlib import Path
from datetime import datetime, timezone

REGISTRY = Path("app/runtime/universal_capability_registry.json")
ABSORPTION_DIR = Path("runtime/capability_absorption")
ABSORPTION_DIR.mkdir(parents=True, exist_ok=True)

def load_registry():
    if not REGISTRY.exists():
        return {"capabilities": {}}
    return json.loads(REGISTRY.read_text(encoding="utf-8"))

def classify_document_text(text: str) -> dict:
    t = (text or "").lower()

    signals = {
        "semantic_retrieval": ["retrieval", "embedding", "pgvector", "semantic search", "neura_embeddings"],
        "social_memory": ["social memory", "memória social", "relationship", "relational"],
        "emotional_report": ["emotion", "emotional", "emoção", "sentimento"],
        "relational_report": ["relational", "relationship", "relacionamento"],
        "semantic_route": ["intent", "router", "semantic_route", "routing"],
        "humanized_answer": ["humanized", "humanização", "humanized_answer"],
        "whatsapp_ux_guard": ["whatsapp", "ux_guard", "guard"],
        "relationalize": ["relationalize", "relacionalizar"],
        "persistent_cognitive_graph": ["graph", "knowledge graph", "cognitive graph", "grafo"],
        "eldora_semantic": ["eldora_semantic", "semantic api", "api semântica"],
    }

    hits = {}

    for cap, terms in signals.items():
        score = sum(1 for term in terms if term in t)
        if score:
            hits[cap] = score

    if not hits:
        return {
            "matched": False,
            "capabilities": [],
            "classification": "NO_CAPABILITY_SIGNAL"
        }

    ranked = sorted(hits.items(), key=lambda x: x[1], reverse=True)

    return {
        "matched": True,
        "capabilities": [
            {"capability": cap, "score": score}
            for cap, score in ranked
        ],
        "classification": "CAPABILITY_SIGNAL_FOUND"
    }

def absorb_text_source(source_id: str, text: str, metadata: dict | None = None) -> dict:
    registry = load_registry()
    known = registry.get("capabilities", {})

    classification = classify_document_text(text)

    rows = []

    for hit in classification.get("capabilities", []):
        cap = hit["capability"]
        reg = known.get(cap, {})

        rows.append({
            "capability": cap,
            "score": hit["score"],
            "registry_status": reg.get("status", "UNKNOWN"),
            "eligible_for_runtime": reg.get("eligible_for_runtime", False),
            "domain": reg.get("domain", "unknown"),
        })

    result = {
        "engine": "P4.76_DRIVE_CAPABILITY_ABSORPTION_ENGINE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_id": source_id,
        "metadata": metadata or {},
        "classification": classification["classification"],
        "matched": classification["matched"],
        "matches": rows,
        "recommended_action": "IGNORE",
    }

    if any(r["eligible_for_runtime"] for r in rows):
        result["recommended_action"] = "QUEUE_FOR_RUNTIME_REVIEW"
    elif rows:
        result["recommended_action"] = "QUEUE_FOR_ADAPTER_REVIEW"

    out = ABSORPTION_DIR / f"{source_id.replace('/', '_').replace(':', '_')}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    return result
