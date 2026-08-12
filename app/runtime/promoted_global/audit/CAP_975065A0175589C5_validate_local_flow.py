import importlib.util
import json
from pathlib import Path
import sys

path = Path("app/api/whatsapp.py")
spec = importlib.util.spec_from_file_location("whatsapp_under_test", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

sender = "P19P21_CERTIFICATION_LOCAL"

flow = [
    "como automatizar confinamento de boi?",
    "como eu faço?",
    "explique melhor",
    "e depois?",
    "aprofunde",
]

results = []

for msg in flow:
    reply = mod.eldora_primary_runtime_reply(sender, msg)
    low = str(reply or "").lower()

    ok = (
        reply is not None
        and "não tenho informação suficiente" not in low
        and "nao tenho informacao suficiente" not in low
        and "sigo no mind" not in low
        and "como posso ajudar" not in low
        and any(x in low for x in [
            "confinamento", "boi", "gado", "silo", "balança", "balanca",
            "cocho", "trato", "bebedouro", "pesagem"
        ])
    )

    results.append({
        "input": msg,
        "reply": reply,
        "pass": ok,
    })

print(json.dumps({
    "mission": "P19P18_P19P19_SHORT_FOLLOWUP_CONTEXT_FIX",
    "all_pass": all(r["pass"] for r in results),
    "results": results,
}, ensure_ascii=False, indent=2))

if not all(r["pass"] for r in results):
    sys.exit(1)
