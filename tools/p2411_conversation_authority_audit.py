import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"

DANGEROUS = [
    "Me dá só o objetivo principal",
    "Entendi. Vou responder de forma prática",
    "Bora com calma e constância",
    "Como posso ajudar hoje",
]

results = []

for path in APP.rglob("*.py"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        for needle in DANGEROUS:
            if needle.lower() in line.lower():
                results.append({
                    "file": str(path),
                    "line": idx,
                    "needle": needle,
                    "text": line.strip(),
                    "severity": "BLOCKER"
                })

out = {
    "mission": "P2411_CONVERSATION_AUTHORITY_COLLAPSE",
    "dangerous_response_templates_found": len(results),
    "status": "PASS" if not results else "BLOCKED",
    "findings": results,
}

print(json.dumps(out, indent=2, ensure_ascii=False))
