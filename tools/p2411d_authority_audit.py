import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"

BAD = ["me dá só o objetivo","entendi. vou responder","bora com calma","como posso ajudar hoje"]
IGNORE = {
    "conversation_authority_contract.py",
    "conversation_authority_hard_guard.py",
    "whatsapp_final_output_guard.py",
    "universal_conversation_os.py",
}

RET = re.compile(r"^\s*return\s+[furbFURB]*['\"].*", re.I)
findings=[]

for path in APP.rglob("*.py"):
    if path.name in IGNORE:
        continue
    for i,line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(),1):
        low=line.lower()
        if RET.search(line) and any(b in low for b in BAD):
            findings.append({"file":str(path),"line":i,"text":line.strip(),"severity":"BLOCKER"})

print(json.dumps({
  "mission":"P2411D",
  "dangerous_direct_returns":len(findings),
  "status":"PASS" if not findings else "BLOCKED",
  "findings":findings
}, indent=2, ensure_ascii=False))
