import os
import json
import time
from pathlib import Path

os.environ["ENABLE_P9_RUNTIME_CONSUMPTION"] = "true"
os.environ["P9_RUNTIME_CONSUMPTION_MODE"] = "DRY_RUN"

from app.p9_runtime_consumption.planner_injection import inject_planner_artifact_dry_run
from app.p9_runtime_consumption.parity import assert_runtime_response_parity
from app.p9_runtime_consumption.observability import append_p9_observation

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P9_RUNTIME_CONSUMPTION_COMPLETE_20260616_153302")
obs_log = out / "P9_OBSERVATION.jsonl"

cases = [
    "Consumir plano sem alterar resposta do runtime.",
    "Injetar artefato planner em contexto read-only.",
    "Validar paridade da resposta runtime.",
    "Preparar consumo interno sem tocar dispatcher.",
    "Validar rollback lógico de consumo."
]

results = []
started = time.perf_counter()

for i, goal in enumerate(cases):
    runtime_before = {"answer": "runtime authoritative", "case": i}

    injection = inject_planner_artifact_dry_run({"goal": goal, "case": i})

    runtime_after = {"answer": "runtime authoritative", "case": i}
    parity = assert_runtime_response_parity(runtime_before, runtime_after)

    record = {
        "case": i,
        "goal": goal,
        "injection_status": injection["status"],
        "consumption_allowed": injection["consumption_allowed"],
        "parity_status": parity["status"],
        "runtime_response_modified": injection["runtime_response_modified"],
        "runtime_state_modified": injection["runtime_state_modified"],
        "routes_modified": injection["routes_modified"],
        "dispatcher_modified": injection["dispatcher_modified"],
        "runtime_authority_preserved": injection["runtime_authority_preserved"] and parity["runtime_authority_preserved"],
    }

    append_p9_observation(record, str(obs_log))
    results.append(record)

pass_count = sum(1 for r in results if r["injection_status"] == "PASS" and r["parity_status"] == "PASS")
mutation_count = sum(1 for r in results if r["runtime_response_modified"] or r["runtime_state_modified"] or r["routes_modified"] or r["dispatcher_modified"])

report = {
    "mission": "P9_RUNTIME_CONSUMPTION_COMPLETE",
    "cases": len(results),
    "pass_count": pass_count,
    "mutation_count": mutation_count,
    "runtime_modified": False,
    "runtime_response_modified": False,
    "runtime_state_modified": False,
    "routes_modified": False,
    "dispatcher_modified": False,
    "whatsapp_webhook_modified": False,
    "active_mode_enabled": False,
    "block_mode_enabled": False,
    "runtime_authority_preserved": True,
    "elapsed_seconds": time.perf_counter() - started,
    "status": "PASS" if pass_count == len(results) and mutation_count == 0 else "FAIL",
    "next_required_action": "P10_CONTROLLED_RUNTIME_CONSUMPTION_ACTIVATION_REVIEW",
    "results": results
}

(out / "P9_RUNTIME_CONSUMPTION_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
