import json
import re
from pathlib import Path

from app.runtime.capability_governance.goal_intent_graph import infer_goal_intent

ROOT = Path.cwd()

SOURCES = {
    "shadow_registry": ROOT / "app/runtime/shadow_registry/registry.json",
    "capability_descriptors": ROOT / "app/runtime/capability_descriptors/capability_runtime_descriptors.json",
    "capability_abstraction": ROOT / "app/runtime/capability_abstraction/capability_abstraction_layer.json",
    "capability_graph": ROOT / "app/runtime/capability_graph/capability_knowledge_graph.json",
    "semantic_contracts": ROOT / "app/runtime/capability_contracts/capability_semantic_contracts.json",
}

INTENT_TO_CAPABILITIES = {
    "design_or_automate_system": {"routing","knowledge_provider","generation","quality_guard","final_authority"},
    "generate_strategy_or_content": {"knowledge_provider","generation","quality_guard","final_authority"},
    "diagnose_or_validate": {"knowledge_provider","diagnostic","quality_guard","final_authority"},
    "continue_current_mission": {"memory","routing","quality_guard","final_authority"},
    "assist": {"knowledge_provider","final_authority"},
}

SOURCE_WEIGHT = {
    "capability_abstraction": 90,
    "capability_descriptors": 75,
    "semantic_contracts": 55,
    "capability_graph": 45,
    "shadow_registry": 35,
}

STOP = {
    "não","para","como","uma","meu","minha","com","sem","que","dos","das",
    "por","the","and","only","runtime","prossiga"
}

def toks(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9áéíóúàãõâêôç_]+", " ", text)
    return set(x for x in text.split() if len(x) >= 3 and x not in STOP)

def load_json(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": str(e)}

def flatten_records(name, data):
    out = []
    if data is None:
        return out

    items = data.items() if isinstance(data, dict) else enumerate(data) if isinstance(data, list) else []
    for k, v in items:
        out.append({
            "source": name,
            "key": str(k),
            "text": json.dumps(v, ensure_ascii=False)[:9000],
            "raw_type": type(v).__name__,
        })
    return out

def universal_frame(query):
    goal = infer_goal_intent(query)
    intent = goal.get("intent", "assist")
    required = set(goal.get("required_capabilities", []))
    outputs = set(goal.get("required_outputs", []))
    abstract = set(INTENT_TO_CAPABILITIES.get(intent, set()))

    return goal, intent, required, outputs, abstract

def coverage_score(blob, intent, required, outputs, abstract):
    blob = blob.lower()
    score = 0
    reasons = []

    if intent and intent in blob:
        score += 120
        reasons.append("intent_match")

    for cap in abstract:
        if cap.lower() in blob:
            score += 90
            reasons.append("abstract:" + cap)

    for req in required:
        if req.lower() in blob:
            score += 70
            reasons.append("required:" + req)

    for out in outputs:
        if out.lower() in blob:
            score += 35
            reasons.append("output:" + out)

    return score, reasons

def lexical_tiebreak(query, blob):
    q = toks(query)
    b = toks(blob)
    overlap = q & b

    if not overlap:
        return 0, []

    return min(20, len(overlap) * 5), ["lexical_tiebreak:" + ",".join(sorted(overlap))]

def retrieve_knowledge(query, limit=12):
    goal, intent, required, outputs, abstract = universal_frame(query)

    records = []
    for name, path in SOURCES.items():
        records.extend(flatten_records(name, load_json(path)))

    ranked = []

    for r in records:
        blob = r["text"] + " " + r["key"] + " " + r["source"]

        score, reasons = coverage_score(blob, intent, required, outputs, abstract)
        lex_score, lex_reasons = lexical_tiebreak(query, blob)

        score += lex_score
        reasons += lex_reasons

        if score <= 0:
            continue

        score += SOURCE_WEIGHT.get(r["source"], 0)

        if score < 120:
            continue

        ranked.append({
            "source": r["source"],
            "key": r["key"],
            "score": score,
            "reasons": reasons[:10],
            "raw_type": r["raw_type"],
            "preview": r["text"][:500],
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    return {
        "query": query,
        "goal_graph": goal,
        "records_scanned": len(records),
        "matches": ranked[:limit],
        "match_count": len(ranked),
        "ranking_policy": "goal_intent_first_lexical_tiebreak_only",
        "mode": "shadow_only",
    }

if __name__ == "__main__":
    tests = [
        "como automatizar confinamento de boi",
        "crie uma estratégia de marketing para eldora",
        "validar runtime trader FTMO paper only",
        "minha Mercedes não entra ré",
        "corrigir resposta do WhatsApp",
        "prossiga",
        "quero vender mais",
        "meu gado está perdendo peso"
    ]

    for t in tests:
        print(json.dumps(retrieve_knowledge(t), indent=2, ensure_ascii=False))
