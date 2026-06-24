import json, re, os
from pathlib import Path

EVID = Path(os.environ["P2401_EVID"])
SRC = Path(os.environ["P2401_SRC_AUDIT"])
EVID.mkdir(parents=True, exist_ok=True)

modules = json.loads((SRC / "01_modules.json").read_text(encoding="utf-8"))
reachable = set(json.loads((SRC / "02_reachable_modules.json").read_text(encoding="utf-8")))
unreachable = set(json.loads((SRC / "03_unreachable_modules.json").read_text(encoding="utf-8")))
response_points = json.loads((SRC / "08_response_authority_points.json").read_text(encoding="utf-8"))

CATS = {
    "ENTRY": ["main", "api", "routes", "webhook", "twilio", "whatsapp"],
    "MEMORY": ["memory", "state", "recall", "remember", "long_term", "semantic"],
    "CONVERSATION": ["conversation", "dialogue", "followup", "continuity", "chat"],
    "INTENT": ["intent", "router", "classifier", "arbitration"],
    "DOMAIN": ["domain", "fitness", "medical", "trader", "automotive", "vision"],
    "PERSONA": ["persona", "personality", "identity"],
    "HUMANIZATION": ["human", "humanization", "natural", "emotion", "affective", "social", "relationship", "friendship", "companionship"],
    "OUTPUT": ["response", "reply", "composer", "guard", "sanitizer", "arbiter", "twiml"],
    "TRAINING": ["training", "simulator", "reward", "dataset"],
    "EXPERIMENTAL": ["shadow", "experimental", "backup", "legacy", "p17", "p18", "p19"],
}

def classify(module, path):
    text = (module + " " + path).lower()
    hits = []
    for cat, words in CATS.items():
        if any(w in text for w in words):
            hits.append(cat)
    return hits or ["OTHER"]

priority_words = [
    "final_conversational_arbiter",
    "humanized_answer_composer",
    "natural_conversation_layer",
    "conversation_state_machine",
    "conversation_continuity_engine",
    "semantic_dialogue_memory",
    "fitness_runtime",
    "universal_domain_router",
    "response_naturalness_score",
    "emotional_continuity_engine",
    "relationship_memory_store",
    "personality_layer",
    "persona_continuity_memory",
    "relational_conversation_engine",
]

rows = []
for m, p in modules.items():
    cats = classify(m, p)
    score = 0
    low = m.lower()
    for i, w in enumerate(priority_words):
        if w in low:
            score += 100 - i
    if any(c in cats for c in ["MEMORY","CONVERSATION","INTENT","DOMAIN","PERSONA","HUMANIZATION","OUTPUT"]):
        score += 10
    if m in reachable:
        score += 5
    rows.append({
        "module": m,
        "path": p,
        "reachable": m in reachable,
        "categories": cats,
        "promotion_score": score,
        "recommended_action": "KEEP_RUNTIME" if m in reachable else ("REVIEW_FOR_PROMOTION" if score >= 10 else "LEGACY_OR_ARCHIVE")
    })

rows_sorted = sorted(rows, key=lambda x: (-x["promotion_score"], x["module"]))

conversation_candidates = [
    r for r in rows_sorted
    if not r["reachable"] and any(c in r["categories"] for c in ["MEMORY","CONVERSATION","INTENT","DOMAIN","PERSONA","HUMANIZATION","OUTPUT"])
]

top_promotion = conversation_candidates[:80]

authority_by_file = {}
for rp in response_points:
    f = rp.get("file", "")
    authority_by_file[f] = authority_by_file.get(f, 0) + 1

duplicate_authority = sorted(
    [{"file": k, "response_authority_points": v} for k,v in authority_by_file.items()],
    key=lambda x: -x["response_authority_points"]
)

summary = {
    "total_modules": len(rows),
    "reachable": sum(1 for r in rows if r["reachable"]),
    "unreachable": sum(1 for r in rows if not r["reachable"]),
    "promotion_candidates_conversation": len(conversation_candidates),
    "top_promotion_list_size": len(top_promotion),
    "files_with_response_authority": len(duplicate_authority),
    "top_response_authority_file": duplicate_authority[0] if duplicate_authority else None,
}

def write(name, data):
    (EVID / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

write("00_summary.json", summary)
write("01_classified_modules.json", rows_sorted)
write("02_conversation_promotion_candidates.json", conversation_candidates)
write("03_top_80_promotion_candidates.json", top_promotion)
write("04_response_authority_by_file.json", duplicate_authority)

md = ["# P2401 Runtime Classification And Promotion Plan\n"]
md.append("## Summary\n```json\n" + json.dumps(summary, ensure_ascii=False, indent=2) + "\n```\n")
md.append("## Top promotion candidates\n")
for r in top_promotion[:30]:
    md.append(f"- {r['module']} | {','.join(r['categories'])} | score={r['promotion_score']} | {r['path']}")
md.append("\n## Strategy\n")
md.append("1. Não ligar tudo automaticamente.\n")
md.append("2. Promover primeiro módulos de memória, domínio, naturalidade e arbiter.\n")
md.append("3. Sovereign Orchestrator continua sendo autoridade única.\n")
md.append("4. Módulos promovidos devem virar providers auxiliares, sem return final direto.\n")
(EVID / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
print("EVIDENCE=", EVID)
