import importlib.util
import json
import sys
from pathlib import Path

path = Path("app/api/whatsapp.py")
spec = importlib.util.spec_from_file_location("whatsapp_under_test", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

flows = {
    "confinamento": [
        "como automatizar confinamento de boi?",
        "como eu faço?",
        "explique melhor",
        "e depois?",
        "aprofunde",
    ],
    "automotivo": [
        "Mercedes Classe A desligado entra marcha ligado não entra",
        "como eu faço?",
        "explique melhor",
        "e depois?",
    ],
    "marketing": [
        "quero criar criativo para campanha no Instagram",
        "como eu faço?",
        "explique melhor",
        "e depois?",
    ],
    "trader": [
        "rodar backtest da estratégia FTMO em paper",
        "como eu faço?",
        "continue",
        "aprofunde",
    ],
}

bad = [
    "não tenho informação suficiente",
    "nao tenho informacao suficiente",
    "como posso ajudar",
    "sigo no mind",
    "me fale mais",
    "preciso de mais contexto",
]

domain_terms = {
    "confinamento": ["confinamento","boi","gado","silo","cocho","trato","bebedouro","pesagem"],
    "automotivo": ["mercedes","embreagem","atuador","marcha","sangria","regulagem","curso"],
    "marketing": ["criativo","campanha","público","publico","gancho","oferta","copy"],
    "trader": ["paper","backtest","drawdown","payoff","simulação","simulacao","ftmo"],
}

results = {}

for domain, messages in flows.items():
    sender = f"P19P21_REAL_CERT_{domain}"
    results[domain] = []

    for msg in messages:
        reply = mod.eldora_primary_runtime_reply(sender, msg)
        low = str(reply or "").lower()

        passed = (
            reply is not None
            and not any(x in low for x in bad)
            and any(x in low for x in domain_terms[domain])
        )

        results[domain].append({
            "input": msg,
            "reply": reply,
            "pass": passed
        })

all_pass = all(x["pass"] for rows in results.values() for x in rows)

print(json.dumps({
    "mission": "P19P21_REAL_WHATSAPP_CERTIFICATION",
    "all_pass": all_pass,
    "results": results,
}, ensure_ascii=False, indent=2))

if not all_pass:
    sys.exit(1)
