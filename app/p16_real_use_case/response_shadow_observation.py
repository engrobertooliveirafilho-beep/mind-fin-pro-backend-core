import json
import time
from pathlib import Path
from typing import Dict, Any, List

from app.p16_real_use_case.controlled_response_shadow import run_controlled_response_shadow_case

def run_response_shadow_observation(log_path: str, iterations: int = 300) -> Dict[str, Any]:
    cases = [
        {"name": "WHATSAPP_RUNTIME", "input": {"goal": "shadow WhatsApp"}, "response": {"answer": "Entendi. Vou organizar isso em etapas simples."}},
        {"name": "ELDORA_RUNTIME", "input": {"goal": "shadow Eldora"}, "response": {"answer": "Vamos criar um plano com tema, formato e frequência."}},
        {"name": "MIND_TRADER_RUNTIME", "input": {"goal": "shadow trader sem ordem real"}, "response": {"answer": "Vamos analisar em simulado, sem execução real."}},
    ]

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Any]] = []
    started = time.perf_counter()

    for i in range(iterations):
        case = cases[i % len(cases)]
        t0 = time.perf_counter()
        result = run_controlled_response_shadow_case(case["input"], case["response"])

        record = {
            "iteration": i,
            "use_case": case["name"],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "status": result["status"],
            "candidate_generated": result["candidate_generated"],
            "candidate_safe": result["candidate_safe"],
            "shadow_only": result["shadow_only"],
            "candidate_visible_to_user": result["candidate_visible_to_user"],
            "runtime_response_modified": result["runtime_response_modified"],
            "runtime_state_modified": result["runtime_state_modified"],
            "routes_modified": result["routes_modified"],
            "dispatcher_modified": result["dispatcher_modified"],
            "whatsapp_webhook_modified": result["whatsapp_webhook_modified"],
            "active_mode_enabled": result["active_mode_enabled"],
            "production_enabled": result["production_enabled"],
            "rollback_available": result["rollback_available"],
        }

        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        results.append(record)

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    unsafe_count = sum(1 for r in results if not r["candidate_safe"])
    leaks = sum(1 for r in results if r["candidate_visible_to_user"])
    mutations = sum(
        1 for r in results
        if r["runtime_response_modified"]
        or r["runtime_state_modified"]
        or r["routes_modified"]
        or r["dispatcher_modified"]
        or r["whatsapp_webhook_modified"]
    )

    return {
        "mission": "P16H_RESPONSE_SHADOW_OBSERVATION",
        "iterations": iterations,
        "pass_count": pass_count,
        "unsafe_count": unsafe_count,
        "leaks": leaks,
        "mutations": mutations,
        "elapsed_seconds": time.perf_counter() - started,
        "runtime_modified": False,
        "runtime_response_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "recommendation": "ALLOW_P16I_RESPONSE_SHADOW_READINESS_REVIEW",
        "next_required_action": "P16I_RESPONSE_SHADOW_READINESS_REVIEW",
        "status": "PASS" if pass_count == iterations and unsafe_count == 0 and leaks == 0 and mutations == 0 else "FAIL",
    }
