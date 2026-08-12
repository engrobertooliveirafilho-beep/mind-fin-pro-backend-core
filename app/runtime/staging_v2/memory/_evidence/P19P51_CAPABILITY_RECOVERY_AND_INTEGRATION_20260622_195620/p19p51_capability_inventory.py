import os, json
from datetime import datetime, timezone

ROOTS = [
    "app/eldora",
    "app/human",
    "app/humanization",
    "app/friendship",
    "app/memory",
    "app/persona",
]

KEYWORDS = {
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

inventory = []

for root in ROOTS:
    if not os.path.exists(root):
        continue

    for base, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".py"):
                continue

            path = os.path.join(base, fn)

            try:
                txt = open(path,"r",encoding="utf-8",errors="ignore").read().lower()
            except:
                txt = ""

            hits = []

            for category, words in KEYWORDS.items():
                if any(w in txt for w in words):
                    hits.append(category)

            if hits:
                inventory.append({
                    "path": path,
                    "categories": sorted(list(set(hits))),
                    "score": len(set(hits))
                })

inventory = sorted(
    inventory,
    key=lambda x:(-x["score"],x["path"])
)

report = {
    "program":"P19P51",
    "created_at":datetime.now(timezone.utc).isoformat(),
    "mode":"CAPABILITY_RECOVERY",
    "roots":ROOTS,
    "modules_found":len(inventory),
    "top_candidates":inventory[:100]
}

print(json.dumps(report,indent=2,ensure_ascii=False))
