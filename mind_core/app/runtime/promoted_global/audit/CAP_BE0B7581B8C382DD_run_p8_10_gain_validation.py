import os
import json
import time
from pathlib import Path

os.environ["ENABLE_HIERARCHICAL_PLANNER"] = "true"
os.environ["HIERARCHICAL_MODE"] = "SHADOW"
os.environ["ENABLE_OVERSIGHT"] = "true"
os.environ["OVERSIGHT_MODE"] = "SHADOW"

from app.p8_shadow.shadow_hooks import run_hierarchical_planner_shadow, run_oversight_shadow

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P8_10_GAIN_VALIDATION_20260616_073333")
telemetry = out / "P8_10_GAIN_TELEMETRY.jsonl"

scenarios = [
    {"goal": "decompose complex user request into execution stages"},
    {"goal": "evaluate whether runtime answer should be allowed reviewed or blocked"},
    {"goal": "prepare multi-step workflow without modifying runtime response"},
    {"goal": "detect divergence between runtime output and governance layer"},
    {"goal": "validate shadow-only cognitive planning capability"}
]

results = []
started = time.perf_counter()

for i in range(200):
    scenario = scenarios[i % len(scenarios)]

    planner = run_hierarchical_planner_shadow(
        {"iteration": i, **scenario},
        log_path=str(telemetry)
    )

    runtime_output = {
        "iteration": i,
        "runtime_answer": "baseline runtime authoritative",
        "scenario": scenario
    }

    oversight = run_oversight_shadow(
        runtime_output,
        log_path=str(telemetry)
    )

    results.append({
        "iteration": i,
        "planner_status": planner.get("mode", planner.get("status")),
        "planner_runtime_modified": planner.get("runtime_modified", False),
        "oversight_mode": oversight.get("mode", oversight.get("status")),
        "oversight_runtime_authority_preserved": oversight.get("runtime_authority_preserved", False),
        "oversight_response_modified": oversight.get("response_modified", False),
        "divergence_score": oversight.get("divergence_score", 0)
    })

elapsed = time.perf_counter() - started

planner_shadow_ok = sum(1 for r in results if r["planner_status"] == "SHADOW")
oversight_shadow_ok = sum(1 for r in results if r["oversight_mode"] == "SHADOW")
runtime_modifications = sum(1 for r in results if r["planner_runtime_modified"] or r["oversight_response_modified"])
authority_preserved = sum(1 for r in results if r["oversight_runtime_authority_preserved"])
divergences = sum(1 for r in results if r["divergence_score"] > 0)

report = {
    "mission": "P8.10_GAIN_VALIDATION",
    "executions": len(results),
    "planner_shadow_ok": planner_shadow_ok,
    "oversight_shadow_ok": oversight_shadow_ok,
    "runtime_modifications": runtime_modifications,
    "authority_preserved": authority_preserved,
    "divergences_detected": divergences,
    "elapsed_seconds": elapsed,
    "avg_seconds_per_execution": elapsed / len(results),
    "planner_gain_status": "STRUCTURAL_CAPABILITY_PRESENT" if planner_shadow_ok == len(results) else "INSUFFICIENT",
    "oversight_gain_status": "AUDIT_CAPABILITY_PRESENT" if oversight_shadow_ok == len(results) else "INSUFFICIENT",
    "cost_status": "ACCEPTABLE" if elapsed / len(results) < 0.05 else "REVIEW_LATENCY",
    "runtime_modified": False,
    "active_mode_allowed": False,
    "block_mode_allowed": False,
    "recommendation": "READY_FOR_P8_11_CONTROLLED_ACTIVE_DRY_RUN" if runtime_modifications == 0 and planner_shadow_ok == len(results) and oversight_shadow_ok == len(results) else "KEEP_SHADOW_FIX_REQUIRED",
    "status": "PASS" if runtime_modifications == 0 and planner_shadow_ok == len(results) and oversight_shadow_ok == len(results) else "FAIL"
}

(out / "P8_10_GAIN_VALIDATION_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
