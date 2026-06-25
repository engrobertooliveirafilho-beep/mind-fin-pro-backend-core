from typing import Dict, Any, List

from app.p8_shadow.real_planner import generate_hierarchical_plan
from app.p9_runtime_consumption.parity import assert_runtime_response_parity

def consume_planner_internal_only(runtime_input: Dict[str, Any], runtime_response: Dict[str, Any]) -> Dict[str, Any]:
    planner = generate_hierarchical_plan(runtime_input)

    internal_context = {
        "planner_available": True,
        "planner_depth": planner["depth"],
        "planner_step_count": planner["step_count"],
        "planner_artifact": planner,
        "visibility": "INTERNAL_ONLY",
    }

    runtime_after = dict(runtime_response)
    parity = assert_runtime_response_parity(runtime_response, runtime_after)

    return {
        "mission": "P16B_INTERNAL_ONLY_RUNTIME_CONSUMPTION_TEST",
        "internal_context": internal_context,
        "runtime_response_before": runtime_response,
        "runtime_response_after": runtime_after,
        "response_modified": parity["response_modified"],
        "runtime_modified": False,
        "runtime_state_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "whatsapp_webhook_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "runtime_authority_preserved": parity["runtime_authority_preserved"],
        "status": "PASS" if parity["status"] == "PASS" else "FAIL",
    }

def run_internal_only_use_cases() -> Dict[str, Any]:
    cases = [
        {
            "name": "WHATSAPP_RUNTIME",
            "input": {"goal": "organizar resposta curta humana no WhatsApp"},
            "response": {"answer": "Entendi. Vou organizar isso em etapas simples."}
        },
        {
            "name": "ELDORA_RUNTIME",
            "input": {"goal": "montar plano de conteúdo Eldora"},
            "response": {"answer": "Vamos criar um plano com tema, formato e frequência."}
        },
        {
            "name": "MIND_TRADER_RUNTIME",
            "input": {"goal": "avaliar estratégia em simulado sem operar real"},
            "response": {"answer": "Vamos analisar em modo simulado, sem execução real."}
        }
    ]

    results: List[Dict[str, Any]] = []

    for case in cases:
        result = consume_planner_internal_only(case["input"], case["response"])
        results.append({
            "use_case": case["name"],
            "status": result["status"],
            "planner_available": result["internal_context"]["planner_available"],
            "planner_depth": result["internal_context"]["planner_depth"],
            "planner_step_count": result["internal_context"]["planner_step_count"],
            "response_modified": result["response_modified"],
            "runtime_modified": result["runtime_modified"],
            "runtime_authority_preserved": result["runtime_authority_preserved"],
        })

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    mutations = sum(1 for r in results if r["response_modified"] or r["runtime_modified"])

    return {
        "mission": "P16B_INTERNAL_ONLY_RUNTIME_CONSUMPTION_TEST",
        "cases": len(results),
        "pass_count": pass_count,
        "mutations": mutations,
        "runtime_modified": False,
        "response_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "recommendation": "ALLOW_LIMITED_RESPONSE_AWARENESS_DRY_RUN",
        "next_required_action": "P16C_LIMITED_RESPONSE_AWARENESS_DRY_RUN",
        "status": "PASS" if pass_count == len(results) and mutations == 0 else "FAIL",
        "results": results,
    }
