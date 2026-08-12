import json
from pathlib import Path

EVID = Path("_evidence/P19P36J_RECOVERED_MEMORY_CONTRACT_AUDIT_20260621_230647")
data = json.loads((EVID / "recovered_memory_contracts.json").read_text(encoding="utf-8"))

rows = []
for c in data["contracts"]:
    mod = c["module"]
    astc = c["ast_contract"]
    rtc = c["runtime_contract"]

    funcs = [f["name"] for f in astc.get("functions", [])]
    classes = [cl["name"] for cl in astc.get("classes", [])]
    experiments = rtc.get("experiments", [])

    ok_exps = [e for e in experiments if e.get("ok")]
    fail_exps = [e for e in experiments if not e.get("ok")]

    can_read = any(
        x in str(ok_exps).lower()
        for x in ["safe_recall", "get", "recall", "load", "search", "resolve_followup", "expand_followup"]
    )
    can_write = any(
        x in str(funcs).lower() + str(classes).lower() + str(ok_exps).lower()
        for x in ["save", "remember", "append", "add", "update_topic_context"]
    )

    if "memory_adapter" in mod:
        decision = "ADAPT_SIGNATURE"
        reason = "safe_recall aceita 1 argumento; adapter atual chamou com 2 em alguns testes."
    elif "memory_store" in mod:
        decision = "CLASS_ADAPTER_REQUIRED"
        reason = "Expõe SimpleMemoryStore; precisa instanciar e mapear métodos reais."
    elif "followup_unified_resolver" in mod:
        decision = "SEED_OR_CONTEXT_REQUIRED"
        reason = "resolve_followup retorna None sem memória/seed; depende de contexto prévio."
    elif "generic_topic_memory_engine" in mod:
        decision = "USE_AS_HELPER_ONLY"
        reason = "Funções existem, mas retornos são fracos em testes; útil como fallback auxiliar."
    elif "vision_memory_store" in mod:
        decision = "DEFER_VISUAL_MEMORY"
        reason = "Fora do fluxo WhatsApp texto por enquanto."
    else:
        decision = "REVIEW"
        reason = "Contrato não classificado."

    rows.append({
        "module": mod,
        "functions": ", ".join(funcs),
        "classes": ", ".join(classes),
        "ok_experiments": len(ok_exps),
        "failed_experiments": len(fail_exps),
        "can_read": can_read,
        "can_write": can_write,
        "decision": decision,
        "reason": reason,
    })

import csv
with open(EVID / "memory_contract_decision_matrix.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

for r in rows:
    print(r)
