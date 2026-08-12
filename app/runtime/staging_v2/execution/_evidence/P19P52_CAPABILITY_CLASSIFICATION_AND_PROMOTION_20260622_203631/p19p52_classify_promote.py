import os, json, ast
from datetime import datetime, timezone

ROOTS = [
    "app/eldora",
    "app/human",
    "app/humanization",
    "app/friendship",
    "app/memory",
    "app/persona",
]

PRIORITY_1 = {
    "app/eldora/core/persistent_social_memory.py",
    "app/eldora/core/relational_cognition_engine.py",
    "app/memory/memory_graph.py",
    "app/persona/human_like_persona_pipeline.py",
    "app/friendship/friendship_profile.py",
}

PRIORITY_2 = {
    "app/eldora/core/recursive_introspection_engine.py",
    "app/persona/persona_continuity_memory.py",
    "app/humanization/social_memory_provider.py",
    "app/humanization/social_pattern_extractor.py",
    "app/humanization/social_observation_layer.py",
}

CATEGORIES = {
    "trust":["trust","confidence","relationship"],
    "attachment":["attachment","bond","friendship"],
    "identity":["identity","persona","profile"],
    "memory":["memory","recall","timeline"],
    "emotion":["emotion","mood","feeling"],
    "reflection":["reflection","introspection"],
    "learning":["learning","adaptation"],
    "planning":["planning","goal","objective"],
    "social":["social","graph","relationship"],
}

def normalize(path):
    return path.replace("\\","/")

def ast_safe(path):
    try:
        ast.parse(open(path,"r",encoding="utf-8",errors="ignore").read())
        return True
    except Exception:
        return False

def extract_exports(path):
    try:
        tree = ast.parse(open(path,"r",encoding="utf-8",errors="ignore").read())
    except Exception:
        return []
    exports = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            exports.append(node.name)
    return exports

items = []

for root in ROOTS:
    if not os.path.exists(root):
        continue

    for base, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".py"):
                continue

            path = normalize(os.path.join(base, fn))
            txt = open(path,"r",encoding="utf-8",errors="ignore").read().lower()

            hits = []
            for cat, words in CATEGORIES.items():
                if any(w in txt for w in words):
                    hits.append(cat)

            if not hits:
                continue

            safe = ast_safe(path)
            exports = extract_exports(path)
            score = len(set(hits))

            if path in PRIORITY_1 and safe:
                decision = "PROMOTE_SHADOW"
            elif path in PRIORITY_2 and safe:
                decision = "PROMOTE_REVIEW"
            elif safe and score >= 3:
                decision = "SHADOW_CANDIDATE"
            elif safe and score >= 1:
                decision = "MANUAL_REVIEW"
            else:
                decision = "REJECT_UNSAFE"

            items.append({
                "path": path,
                "categories": sorted(set(hits)),
                "score": score,
                "ast_safe": safe,
                "exports": exports[:20],
                "decision": decision,
            })

items = sorted(items, key=lambda x: (
    {"PROMOTE_SHADOW":0,"PROMOTE_REVIEW":1,"SHADOW_CANDIDATE":2,"MANUAL_REVIEW":3,"REJECT_UNSAFE":4}.get(x["decision"],9),
    -x["score"],
    x["path"]
))

summary = {}
for item in items:
    summary[item["decision"]] = summary.get(item["decision"], 0) + 1

report = {
    "program":"P19P52",
    "created_at":datetime.now(timezone.utc).isoformat(),
    "mode":"CLASSIFICATION_AND_SHADOW_PROMOTION_PLAN",
    "runtime_mutation":False,
    "response_mutation":False,
    "production_enabled":False,
    "modules_total":len(items),
    "summary":summary,
    "items":items,
}

print(json.dumps(report, indent=2, ensure_ascii=False))
