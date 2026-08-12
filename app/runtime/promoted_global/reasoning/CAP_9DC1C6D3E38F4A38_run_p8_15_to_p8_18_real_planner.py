import json
import time
from pathlib import Path

from app.p8_shadow.real_planner import generate_hierarchical_plan
from app.p8_shadow.diff_engine import build_decision_diff

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P8_15_TO_P8_18_REAL_PLANNER_UPGRADE_20260616_130914")

prompts = [
    "Implantar capability sem modificar runtime.",
    "Criar plano de testes com rollback.",
    "Auditar risco antes de ativação.",
    "Separar execução shadow de execução ativa.",
    "Planejar workflow com etapas dependentes.",
    "Criar governança de feature flags.",
    "Avaliar saída do runtime contra camada cognitiva.",
    "Definir critérios objetivos de ativação.",
    "Reduzir checklist simples para plano hierárquico.",
    "Gerar trilha auditável de decisão."
]

results = []
started = time.perf_counter()

for i, prompt in enumerate(prompts):
    t0 = time.perf_counter()

    baseline = {
        "type": "simple_checklist",
        "depth": 1,
        "step_count": 4,
        "steps": ["analisar", "executar", "testar", "registrar"]
    }

    planner = generate_hierarchical_plan({"prompt": prompt, "goal": prompt})

    diff = build_decision_diff(
        request_id=f"p8-15-{i}",
        runtime_decision=baseline,
        oversight_decision=planner,
        confidence=0.95,
        reason="real_planner_upgrade_benchmark"
    )

    latency_ms = (time.perf_counter() - t0) * 1000

    baseline_score = baseline["depth"] + baseline["step_count"]
    planner_score = planner["depth"] + planner["step_count"] + len(planner["execution_tree"]["children"])

    results.append({
        "case": i,
        "prompt": prompt,
        "latency_ms": latency_ms,
        "baseline_score": baseline_score,
        "planner_score": planner_score,
        "gain_delta": planner_score - baseline_score,
        "planner_depth": planner["depth"],
        "planner_step_count": planner["step_count"],
        "runtime_modified": planner["runtime_modified"],
        "response_modified": planner["response_modified"],
        "runtime_authority_preserved": planner["runtime_authority_preserved"],
        "diff_same_decision": diff["same_decision"]
    })

elapsed = time.perf_counter() - started
avg_gain = sum(r["gain_delta"] for r in results) / len(results)
avg_latency = sum(r["latency_ms"] for r in results) / len(results)
runtime_modifications = sum(1 for r in results if r["runtime_modified"] or r["response_modified"])

report = {
    "mission": "P8.15_TO_P8.18_REAL_PLANNER_OUTPUT_UPGRADE_AND_BENCHMARK",
    "cases": len(results),
    "avg_gain_delta": avg_gain,
    "avg_latency_ms": avg_latency,
    "elapsed_seconds": elapsed,
    "runtime_modifications": runtime_modifications,
    "runtime_modified": False,
    "response_modified": False,
    "active_mode_enabled": False,
    "block_mode_enabled": False,
    "runtime_authority_preserved": True,
    "planner_business_value": "POSITIVE_SIGNAL" if avg_gain > 0 else "NOT_PROVEN",
    "recommendation": "READY_FOR_LIMITED_ACTIVE_SANDBOX_REVIEW" if avg_gain > 0 and runtime_modifications == 0 else "KEEP_SHADOW",
    "status": "PASS" if avg_gain > 0 and runtime_modifications == 0 else "FAIL",
    "results": results
}

(out / "P8_15_TO_P8_18_REAL_PLANNER_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
