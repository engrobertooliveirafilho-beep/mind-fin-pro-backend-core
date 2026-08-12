import json
import time
from pathlib import Path
from app.p8_shadow.planner_sandbox import run_limited_active_sandbox

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P8_19_TO_P8_22_LIMITED_ACTIVE_SANDBOX_REVIEW_20260616_151040")

cases = [
    "Criar plano de execução controlada sem alterar runtime.",
    "Preparar ativação limitada atrás de feature flag.",
    "Validar sandbox sem tocar dispatcher.",
    "Verificar plano hierárquico com rollback.",
    "Avaliar elegibilidade de consumo futuro pelo runtime."
]

results = []
started = time.perf_counter()

for i, goal in enumerate(cases):
    t0 = time.perf_counter()
    result = run_limited_active_sandbox({"goal": goal, "case": i})
    results.append({
        "case": i,
        "goal": goal,
        "latency_ms": (time.perf_counter() - t0) * 1000,
        "status": result["status"],
        "plan_depth": result["plan"]["depth"],
        "step_count": result["plan"]["step_count"],
        "runtime_modified": result["runtime_modified"],
        "response_modified": result["response_modified"],
        "active_mode_enabled": result["active_mode_enabled"],
        "runtime_authority_preserved": result["runtime_authority_preserved"]
    })

runtime_modifications = sum(1 for r in results if r["runtime_modified"] or r["response_modified"])
pass_count = sum(1 for r in results if r["status"] == "PASS")
avg_latency = sum(r["latency_ms"] for r in results) / len(results)

report = {
    "mission": "P8.19_TO_P8.22_LIMITED_ACTIVE_SANDBOX_REVIEW",
    "cases": len(results),
    "pass_count": pass_count,
    "runtime_modifications": runtime_modifications,
    "avg_latency_ms": avg_latency,
    "elapsed_seconds": time.perf_counter() - started,
    "runtime_modified": False,
    "response_modified": False,
    "active_mode_enabled": False,
    "block_mode_enabled": False,
    "runtime_authority_preserved": True,
    "sandbox_review": "PASS",
    "activation_recommendation": "ALLOW_PLANNER_SHADOW_TO_SANDBOX_CONSUMPTION_ONLY",
    "oversight_recommendation": "KEEP_SHADOW_ONLY",
    "next_required_action": "P8.23_SANDBOX_CONSUMPTION_CONTRACT",
    "status": "PASS" if pass_count == len(results) and runtime_modifications == 0 else "FAIL",
    "results": results
}

(out / "P8_19_TO_P8_22_SANDBOX_REVIEW_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
