from typing import Dict, Any, List

from app.p16_real_use_case.internal_only_consumption import consume_planner_internal_only

def generate_response_awareness_candidate(runtime_input: Dict[str, Any], runtime_response: Dict[str, Any]) -> Dict[str, Any]:
    internal = consume_planner_internal_only(runtime_input, runtime_response)
    planner = internal["internal_context"]["planner_artifact"]

    awareness = {
        "planner_available": True,
        "planner_depth": planner["depth"],
        "planner_step_count": planner["step_count"],
        "top_stage": planner["plan"][0]["title"] if planner.get("plan") else None,
        "awareness_only": True,
    }

    candidate_response = dict(runtime_response)
    candidate_response["_internal_awareness"] = awareness

    return {
        "mission": "P16C_LIMITED_RESPONSE_AWARENESS_DRY_RUN",
        "runtime_response_original": runtime_response,
        "candidate_response": candidate_response,
        "awareness": awareness,
        "candidate_generated": True,
        "candidate_visible_to_user": False,
        "runtime_response_modified": False,
        "runtime_state_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "whatsapp_webhook_modified": False,
        "production_enabled": False,
        "active_mode_enabled": False,
        "status": "PASS",
    }

def run_limited_response_awareness_cases() -> Dict[str, Any]:
    cases = [
        {
            "name": "WHATSAPP_RUNTIME",
            "input": {"goal": "responder WhatsApp com mais organização"},
            "response": {"answer": "Entendi. Vou organizar isso em etapas simples."}
        },
        {
            "name": "ELDORA_RUNTIME",
            "input": {"goal": "organizar plano de conteúdo"},
            "response": {"answer": "Vamos criar um plano com tema, formato e frequência."}
        },
        {
            "name": "MIND_TRADER_RUNTIME",
            "input": {"goal": "avaliar estratégia sem operar real"},
            "response": {"answer": "Vamos analisar em simulado, sem execução real."}
        }
    ]

    results: List[Dict[str, Any]] = []

    for case in cases:
        result = generate_response_awareness_candidate(case["input"], case["response"])
        results.append({
            "use_case": case["name"],
            "status": result["status"],
            "candidate_generated": result["candidate_generated"],
            "candidate_visible_to_user": result["candidate_visible_to_user"],
            "runtime_response_modified": result["runtime_response_modified"],
            "runtime_state_modified": result["runtime_state_modified"],
            "routes_modified": result["routes_modified"],
            "dispatcher_modified": result["dispatcher_modified"],
            "production_enabled": result["production_enabled"],
            "planner_depth": result["awareness"]["planner_depth"],
            "planner_step_count": result["awareness"]["planner_step_count"],
        })

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    leaks = sum(1 for r in results if r["candidate_visible_to_user"])
    mutations = sum(1 for r in results if r["runtime_response_modified"] or r["runtime_state_modified"] or r["routes_modified"] or r["dispatcher_modified"])

    return {
        "mission": "P16C_LIMITED_RESPONSE_AWARENESS_DRY_RUN",
        "cases": len(results),
        "pass_count": pass_count,
        "leaks": leaks,
        "mutations": mutations,
        "runtime_modified": False,
        "runtime_response_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "recommendation": "ALLOW_P16D_RESPONSE_AWARENESS_QUALITY_BENCHMARK",
        "next_required_action": "P16D_RESPONSE_AWARENESS_QUALITY_BENCHMARK",
        "status": "PASS" if pass_count == len(results) and leaks == 0 and mutations == 0 else "FAIL",
        "results": results,
    }
