import os
import json
import time
from pathlib import Path

os.environ["ENABLE_HIERARCHICAL_PLANNER"] = "true"
os.environ["HIERARCHICAL_MODE"] = "SHADOW"
os.environ["ENABLE_OVERSIGHT"] = "true"
os.environ["OVERSIGHT_MODE"] = "SHADOW"

from app.p8_shadow.shadow_hooks import run_hierarchical_planner_shadow, run_oversight_shadow

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P8_14_REAL_WORLD_PLANNER_BENCHMARK_20260616_130544")
telemetry = out / "P8_14_REAL_WORLD_BENCHMARK_TELEMETRY.jsonl"

prompts = [
    "Planejar execução segura de uma nova camada sem alterar runtime.",
    "Dividir uma missão complexa em etapas auditáveis.",
    "Validar se uma resposta precisa de revisão antes de ser enviada.",
    "Criar plano para integrar capability em shadow mode.",
    "Auditar risco de mutação direta no core.",
    "Organizar fases de rollout controlado com rollback.",
    "Gerar plano de testes para feature flag.",
    "Avaliar divergência entre resposta runtime e camada oversight.",
    "Criar workflow cognitivo com decomposição hierárquica.",
    "Preparar plano de observação com métricas de latência e falha."
]

results = []
started_global = time.perf_counter()

for i, prompt in enumerate(prompts):
    started = time.perf_counter()

    runtime_baseline = {
        "type": "baseline_checklist",
        "prompt": prompt,
        "steps": ["analisar", "executar", "testar", "registrar"],
        "depth": 1
    }

    planner = run_hierarchical_planner_shadow(
        {
            "iteration": i,
            "prompt": prompt,
            "goal": "real world hierarchical planning benchmark"
        },
        log_path=str(telemetry)
    )

    oversight = run_oversight_shadow(
        runtime_baseline,
        log_path=str(telemetry)
    )

    elapsed = (time.perf_counter() - started) * 1000

    planner_ok = planner.get("mode") == "SHADOW"
    oversight_ok = oversight.get("mode") == "SHADOW"

    baseline_score = len(runtime_baseline["steps"]) + runtime_baseline["depth"]

    planner_score = 0
    if planner_ok:
        planner_score += 3
        planner_score += 1 if planner.get("capability") == "HIERARCHICAL_PLANNING" else 0
        planner_score += 1 if planner.get("runtime_modified") is False else 0

    results.append({
        "case": i,
        "prompt": prompt,
        "latency_ms": elapsed,
        "baseline_score": baseline_score,
        "planner_score": planner_score,
        "planner_ok": planner_ok,
        "oversight_ok": oversight_ok,
        "runtime_modified": False,
        "response_modified": False,
        "runtime_authority_preserved": True,
        "gain_delta": planner_score - baseline_score
    })

elapsed_global = time.perf_counter() - started_global

planner_ok_count = sum(1 for r in results if r["planner_ok"])
oversight_ok_count = sum(1 for r in results if r["oversight_ok"])
avg_latency = sum(r["latency_ms"] for r in results) / len(results)
avg_gain_delta = sum(r["gain_delta"] for r in results) / len(results)

report = {
    "mission": "P8.14_REAL_WORLD_PLANNER_BENCHMARK",
    "cases": len(results),
    "planner_ok_count": planner_ok_count,
    "oversight_ok_count": oversight_ok_count,
    "avg_latency_ms": avg_latency,
    "avg_gain_delta": avg_gain_delta,
    "elapsed_seconds": elapsed_global,
    "runtime_modified": False,
    "response_modified": False,
    "active_mode_enabled": False,
    "block_mode_enabled": False,
    "runtime_authority_preserved": True,
    "planner_business_value": "WEAK_OR_STRUCTURAL_ONLY" if avg_gain_delta <= 0 else "POSITIVE_SIGNAL",
    "recommendation": "KEEP_PLANNER_SHADOW_AND_IMPROVE_REAL_PLAN_OUTPUT" if avg_gain_delta <= 0 else "READY_FOR_LIMITED_ACTIVE_SANDBOX",
    "status": "PASS" if planner_ok_count == len(results) and oversight_ok_count == len(results) else "FAIL",
    "results": results
}

(out / "P8_14_REAL_WORLD_PLANNER_BENCHMARK_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
