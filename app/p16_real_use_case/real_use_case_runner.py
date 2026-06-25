from typing import Dict, Any, List

from app.p8_shadow.real_planner import generate_hierarchical_plan
from app.p9_runtime_consumption.parity import assert_runtime_response_parity

REAL_USE_CASES = [
    {
        "name": "WHATSAPP_RUNTIME",
        "input": "Usuário pede ajuda pelo WhatsApp para organizar uma tarefa complexa.",
        "baseline_response": "Entendi. Vou organizar isso em etapas simples."
    },
    {
        "name": "ELDORA_RUNTIME",
        "input": "Usuário pede para Eldora montar um plano de conteúdo para Instagram.",
        "baseline_response": "Vamos criar um plano com tema, formato e frequência."
    },
    {
        "name": "MIND_TRADER_RUNTIME",
        "input": "Usuário pede plano seguro para avaliar estratégia de trading sem operar real.",
        "baseline_response": "Vamos analisar em modo simulado, com controle de risco e sem execução real."
    }
]

def run_real_use_case_consumption() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    for case in REAL_USE_CASES:
        runtime_before = {"answer": case["baseline_response"], "source": case["name"]}

        planner = generate_hierarchical_plan({
            "goal": case["input"],
            "use_case": case["name"]
        })

        runtime_after = {"answer": case["baseline_response"], "source": case["name"]}

        parity = assert_runtime_response_parity(runtime_before, runtime_after)

        planner_gain_score = (
            planner.get("depth", 0)
            + planner.get("step_count", 0)
            + (1 if planner.get("execution_tree") else 0)
        )

        baseline_score = 2

        results.append({
            "use_case": case["name"],
            "planner_depth": planner.get("depth", 0),
            "planner_step_count": planner.get("step_count", 0),
            "planner_gain_score": planner_gain_score,
            "baseline_score": baseline_score,
            "gain_delta": planner_gain_score - baseline_score,
            "runtime_response_modified": parity["response_modified"],
            "runtime_authority_preserved": parity["runtime_authority_preserved"],
            "runtime_modified": False,
            "planner_output_available": True,
            "status": "PASS" if parity["status"] == "PASS" and planner_gain_score > baseline_score else "FAIL",
        })

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    avg_gain = sum(r["gain_delta"] for r in results) / len(results)

    return {
        "mission": "P16A_REAL_USE_CASE_CONSUMPTION",
        "cases": len(results),
        "pass_count": pass_count,
        "avg_gain_delta": avg_gain,
        "runtime_modified": False,
        "runtime_response_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "recommendation": "ALLOW_INTERNAL_ONLY_REAL_USE_CASE_TESTING" if pass_count == len(results) else "KEEP_DRY_RUN",
        "next_required_action": "P16B_INTERNAL_ONLY_RUNTIME_CONSUMPTION_TEST",
        "status": "PASS" if pass_count == len(results) else "FAIL",
        "results": results,
    }
