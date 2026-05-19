from pathlib import Path
import json

p=Path("app/api/whatsapp.py")
s=p.read_text(encoding="utf-8")
lines=s.splitlines()

keys=[
    "Digite APROFUNDAR",
    "APROFUNDAR",
    "return twiml(",
    "<Message>",
    "eldora_primary_runtime_reply",
    "run_cognitive_pipeline",
    "semantic_test_injection",
    "PROD_STATE_GUARD_DIRECT",
    "build_mind_state_visible_response",
    "twiml("
]

hits={}

for k in keys:
    out=[]
    for i,l in enumerate(lines,start=1):
        if k.lower() in l.lower():
            out.append({
                "line": i,
                "text": l[:300]
            })
    hits[k]=out

print(json.dumps(hits,indent=2,ensure_ascii=False))
