import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
WHATSAPP = ROOT / "app" / "api" / "whatsapp.py"

text = WHATSAPP.read_text(encoding="utf-8", errors="ignore")
lines = text.splitlines()

signals = {
    "imports_collapse_authority": "collapse_authority" in text,
    "imports_provider_candidate": "ProviderCandidate" in text,
    "uses_authority_decision": "AuthorityDecision" in text,
    "twiml_final_text": bool(re.search(r"twiml\s*\(\s*.*final_text", text)),
    "direct_twiML_answer": bool(re.search(r"twiml\s*\(\s*answer\s*\)", text)),
    "return_response_count": len(re.findall(r"return\s+Response\s*\(", text)),
    "return_string_count": len(re.findall(r"return\s+[furbFURB]*['\"]", text)),
}

execution_points = []
for i, line in enumerate(lines, 1):
    low = line.lower()
    if "return response" in low or "twiml(" in low or re.search(r"^\s*return\s+", line):
        safe_line = line.strip().encode("utf-8", errors="replace").decode("utf-8", errors="replace")
        execution_points.append({"line": i, "text": safe_line})

status = "PASS" if (
    signals["imports_collapse_authority"]
    and signals["imports_provider_candidate"]
    and signals["twiml_final_text"]
    and signals["return_response_count"] == 1
    and signals["return_string_count"] == 0
) else "BLOCKED"

out = {
    "mission": "P2411F2",
    "file": str(WHATSAPP),
    "status": status,
    "signals": signals,
    "execution_points": execution_points,
}

print(json.dumps(out, indent=2, ensure_ascii=False))
