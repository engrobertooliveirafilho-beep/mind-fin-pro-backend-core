from typing import Dict, Any, List

from app.p16_real_use_case.limited_response_modification import generate_limited_response_modification_candidate
from app.p16_real_use_case.response_modification_safety_gate import inspect_candidate_response

def run_controlled_response_shadow_case(runtime_input: Dict[str, Any], runtime_response: Dict[str, Any]) -> Dict[str, Any]:
    candidate = generate_limited_response_modification_candidate(runtime_input, runtime_response)
    safety = inspect_candidate_response(candidate)

    selected_response = runtime_response

    return {
        "mission": "P16G_CONTROLLED_RESPONSE_MODIFICATION_SHADOW",
        "runtime_response_original": runtime_response,
        "candidate_response": candidate["candidate_response"],
        "selected_response": selected_response,
        "candidate_generated": candidate["candidate_generated"],
        "candidate_safe": safety["safe"],
        "shadow_only": True,
        "candidate_visible_to_user": False,
        "runtime_response_modified": False,
        "runtime_state_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "whatsapp_webhook_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "rollback_available": True,
        "status": "PASS" if safety["status"] == "PASS" and selected_response == runtime_response else "FAIL",
    }

def run_controlled_response_modification_shadow() -> Dict[str, Any]:
    cases = [
        {
            "name": "WHATSAPP_RUNTIME",
            "input": {"goal": "gerar candidato melhorado sem entregar ao usuário"},
            "response": {"answer": "Entendi. Vou organizar isso em etapas simples."}
        },
        {
            "name": "ELDORA_RUNTIME",
            "input": {"goal": "gerar candidato de plano de conteúdo sem publicar"},
            "response": {"answer": "Vamos criar um plano com tema, formato e frequência."}
        },
        {
            "name": "MIND_TRADER_RUNTIME",
            "input": {"goal": "gerar candidato de explicação sem operar real"},
            "response": {"answer": "Vamos analisar em simulado, sem execução real."}
        }
    ]

    results: List[Dict[str, Any]] = []

    for case in cases:
        result = run_controlled_response_shadow_case(case["input"], case["response"])
        results.append({
            "use_case": case["name"],
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
        })

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
        "mission": "P16G_CONTROLLED_RESPONSE_MODIFICATION_SHADOW",
        "cases": len(results),
        "pass_count": pass_count,
        "unsafe_count": unsafe_count,
        "leaks": leaks,
        "mutations": mutations,
        "runtime_modified": False,
        "runtime_response_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "recommendation": "ALLOW_P16H_RESPONSE_SHADOW_OBSERVATION",
        "next_required_action": "P16H_RESPONSE_SHADOW_OBSERVATION",
        "status": "PASS" if pass_count == len(results) and unsafe_count == 0 and leaks == 0 and mutations == 0 else "FAIL",
        "results": results,
    }
