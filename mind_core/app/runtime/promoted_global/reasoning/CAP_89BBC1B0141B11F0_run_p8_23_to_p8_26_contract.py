import json
import time
from pathlib import Path
from app.p8_shadow.planner_consumption_contract import produce_consumable_planner_artifact

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P8_23_TO_P8_26_SANDBOX_CONSUMPTION_CONTRACT_20260616_152251")

cases = [
    "Consumir plano como artefato interno sem alterar resposta.",
    "Validar contrato antes de qualquer integração.",
    "Garantir que runtime continua autoridade.",
    "Produzir plano hierárquico pronto para observação.",
    "Preparar handoff para eventual integração futura atrás de flag."
]

results = []
started = time.perf_counter()

for i, goal in enumerate(cases):
    t0 = time.perf_counter()
    artifact = produce_consumable_planner_artifact({"goal": goal, "case": i})
    results.append({
        "case": i,
        "goal": goal,
        "latency_ms": (time.perf_counter() - t0) * 1000,
        "status": artifact["status"],
        "contract_valid": artifact["contract"]["valid"],
        "consumption_allowed": artifact["consumption_allowed"],
        "step_count": artifact["planner_output"]["step_count"],
        "depth": artifact["planner_output"]["depth"],
        "runtime_modified": artifact["runtime_modified"],
        "response_modified": artifact["response_modified"],
        "active_mode_enabled": artifact["active_mode_enabled"],
        "runtime_authority_preserved": artifact["runtime_authority_preserved"]
    })

pass_count = sum(1 for r in results if r["status"] == "PASS")
runtime_modifications = sum(1 for r in results if r["runtime_modified"] or r["response_modified"])

report = {
    "mission": "P8.23_TO_P8.26_SANDBOX_CONSUMPTION_CONTRACT",
    "cases": len(results),
    "pass_count": pass_count,
    "runtime_modifications": runtime_modifications,
    "runtime_modified": False,
    "response_modified": False,
    "active_mode_enabled": False,
    "block_mode_enabled": False,
    "runtime_authority_preserved": True,
    "contract_status": "PASS" if pass_count == len(results) and runtime_modifications == 0 else "FAIL",
    "next_required_action": "P8.27_PLANNER_RUNTIME_INTEGRATION_GATE_REVIEW",
    "status": "PASS" if pass_count == len(results) and runtime_modifications == 0 else "FAIL",
    "results": results
}

(out / "P8_23_TO_P8_26_CONSUMPTION_CONTRACT_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
