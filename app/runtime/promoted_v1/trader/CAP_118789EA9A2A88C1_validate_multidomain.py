import importlib.util
import json
import sys
from pathlib import Path

path = Path("app/api/whatsapp.py")
spec = importlib.util.spec_from_file_location("whatsapp_under_test", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

cases = {
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

must_contain = {
    "confinamento": ["confinamento", "boi", "silo", "cocho", "trato", "bebedouro", "pesagem"],
    "automotivo": ["embreagem", "atuador", "marcha", "sangria", "regulagem", "curso"],
    "marketing": ["público", "publico", "criativo", "campanha", "gancho", "oferta"],
    "trader": ["paper", "backtest", "drawdown", "payoff", "simulação", "simulacao"],
}

results = {}

for domain, flow in cases.items():
    sender = f"P19P20_{domain}"
    domain_results = []

    for msg in flow:
        reply = mod.eldora_primary_runtime_reply(sender, msg)
        low = str(reply or "").lower()

        ok = (
            reply is not None
            and "não tenho informação suficiente" not in low
            and "nao tenho informacao suficiente" not in low
            and "sigo no mind" not in low
            and "como posso ajudar" not in low
            and any(x in low for x in must_contain[domain])
        )

        domain_results.append({
            "input": msg,
            "reply": reply,
            "pass": ok,
        })

    results[domain] = domain_results

all_pass = all(item["pass"] for rows in results.values() for item in rows)

print(json.dumps({
    "mission": "P19P20_MULTI_DOMAIN_CONTINUITY_CERTIFICATION",
    "all_pass": all_pass,
    "results": results,
}, ensure_ascii=False, indent=2))

if not all_pass:
    sys.exit(1)
