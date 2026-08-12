import json
import os
from datetime import datetime, timezone

ROOTS = [
    "app/eldora",
    "app/human",
    "app/humanization",
    "app/friendship",
    "app/memory",
    "app/persona",
]

KEYWORDS = [
    "trust",
    "attachment",
    "relationship",
    "social",
    "timeline",
    "preference",
    "identity",
    "mood",
    "reflection",
    "hypothesis",
    "belief",
    "contradiction",
    "learning",
    "planning",
]

matches = []

for root in ROOTS:
    if not os.path.exists(root):
        continue
    for base, _, files in os.walk(root):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(base, file)
            try:
                text = open(path, "r", encoding="utf-8", errors="ignore").read().lower()
            except Exception:
                text = ""
            hits = [kw for kw in KEYWORDS if kw in text or kw in path.lower()]
            if hits:
                matches.append({
                    "path": path,
                    "hits": hits,
                })

report = {
    "program": "P19P49",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "scan_roots": ROOTS,
    "keyword_matches": matches,
    "match_count": len(matches),
    "mode": "INVENTORY_ONLY",
    "runtime_mutation": False,
    "response_mutation": False,
}

print(json.dumps(report, indent=2, ensure_ascii=False))
