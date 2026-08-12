import importlib.util
import json
import sys
from pathlib import Path

path = Path("app/api/whatsapp.py")
spec = importlib.util.spec_from_file_location("whatsapp_under_test", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

flow = [
    "como posso automatizar meu confinamento de boi, para não precisar de funcionario?",
    "como eu faço?",
    "explique melhor",
    "como fazer?",
    "vc esta mto superficial",
]

sender = "whatsapp:+5519999999999"
results = []

bad = [
    "invista em alimentadores automáticos",
    "invista em alimentadores automaticos",
    "considere os seguintes passos",
    "não tenho informação suficiente",
    "nao tenho informacao suficiente",
    "como posso ajudar",
    "me fale mais",
    "sigo no mind",
]

good = [
    "silo", "balança", "balanca", "cocho", "trato", "bebedouro",
    "pesagem", "água", "agua", "dashboard", "alerta", "misturador"
]

for msg in flow:
    reply = mod._p19p21b_real_whatsapp_certified_reply(sender, msg)
    low = str(reply or "").lower()

    passed = (
        reply is not None
        and not any(x in low for x in bad)
        and any(x in low for x in good)
    )

    results.append({
        "input": msg,
        "reply": reply,
        "pass": passed,
    })

all_pass = all(r["pass"] for r in results)

print(json.dumps({
    "mission": "P19P21B_REAL_WHATSAPP_EXECUTION_PATH_AUDIT_AND_PATCH",
    "all_pass": all_pass,
    "results": results
}, ensure_ascii=False, indent=2))

if not all_pass:
    sys.exit(1)
