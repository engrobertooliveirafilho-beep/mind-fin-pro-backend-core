from typing import Dict, Any, List

from app.p16_real_use_case.limited_response_modification import generate_limited_response_modification_candidate

FORBIDDEN_PATTERNS = [
    "_internal_awareness",
    "planner_artifact",
    "internal_context",
    "runtime_authority_preserved",
    "dispatcher_modified",
    "routes_modified",
    "whatsapp_webhook_modified",
]

def inspect_candidate_response(candidate: Dict[str, Any]) -> Dict[str, Any]:
    response = candidate.get("candidate_response", {})
    response_text = str(response)

    leaks = [pattern for pattern in FORBIDDEN_PATTERNS if pattern in response_text]

    original = candidate.get("runtime_response_original", {})
    modified = candidate.get("candidate_response", {})

    answer_original = str(original.get("answer", ""))
    answer_modified = str(modified.get("answer", ""))

    delta_len = len(answer_modified) - len(answer_original)

    safe = (
        candidate.get("candidate_visible_to_user") is False
        and candidate.get("runtime_response_modified") is False
        and candidate.get("runtime_state_modified") is False
        and candidate.get("routes_modified") is False
        and candidate.get("dispatcher_modified") is False
        and candidate.get("whatsapp_webhook_modified") is False
        and len(leaks) == 0
        and delta_len >= 0
        and delta_len <= 160
    )

    return {
        "mission": "P16F_RESPONSE_MODIFICATION_SAFETY_GATE",
        "safe": safe,
        "leaks": leaks,
        "delta_len": delta_len,
        "candidate_visible_to_user": candidate.get("candidate_visible_to_user"),
        "runtime_response_modified": candidate.get("runtime_response_modified"),
        "runtime_state_modified": candidate.get("runtime_state_modified"),
        "routes_modified": candidate.get("routes_modified"),
        "dispatcher_modified": candidate.get("dispatcher_modified"),
        "whatsapp_webhook_modified": candidate.get("whatsapp_webhook_modified"),
        "rollback_available": candidate.get("rollback_available"),
        "status": "PASS" if safe else "FAIL",
    }

def run_response_modification_safety_gate() -> Dict[str, Any]:
    cases = [
        {
            "name": "WHATSAPP_RUNTIME",
            "input": {"goal": "melhorar resposta sem expor camada interna"},
            "response": {"answer": "Entendi. Vou organizar isso em etapas simples."}
        },
        {
            "name": "ELDORA_RUNTIME",
            "input": {"goal": "melhorar clareza do plano de conteúdo"},
            "response": {"answer": "Vamos criar um plano com tema, formato e frequência."}
        },
        {
            "name": "MIND_TRADER_RUNTIME",
            "input": {"goal": "melhorar explicação sem execução real"},
            "response": {"answer": "Vamos analisar em simulado, sem execução real."}
        }
    ]

    results: List[Dict[str, Any]] = []

    for case in cases:
        candidate = generate_limited_response_modification_candidate(case["input"], case["response"])
        safety = inspect_candidate_response(candidate)

        results.append({
            "use_case": case["name"],
            "status": safety["status"],
            "safe": safety["safe"],
            "leaks": safety["leaks"],
            "delta_len": safety["delta_len"],
            "candidate_visible_to_user": safety["candidate_visible_to_user"],
            "runtime_response_modified": safety["runtime_response_modified"],
            "runtime_state_modified": safety["runtime_state_modified"],
            "routes_modified": safety["routes_modified"],
            "dispatcher_modified": safety["dispatcher_modified"],
            "whatsapp_webhook_modified": safety["whatsapp_webhook_modified"],
            "rollback_available": safety["rollback_available"],
        })

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    leak_count = sum(len(r["leaks"]) for r in results)
    mutation_count = sum(
        1 for r in results
        if r["runtime_response_modified"]
        or r["runtime_state_modified"]
        or r["routes_modified"]
        or r["dispatcher_modified"]
        or r["whatsapp_webhook_modified"]
    )

    return {
        "mission": "P16F_RESPONSE_MODIFICATION_SAFETY_GATE",
        "cases": len(results),
        "pass_count": pass_count,
        "leak_count": leak_count,
        "mutation_count": mutation_count,
        "runtime_modified": False,
        "runtime_response_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "recommendation": "ALLOW_P16G_CONTROLLED_RESPONSE_MODIFICATION_SHADOW",
        "next_required_action": "P16G_CONTROLLED_RESPONSE_MODIFICATION_SHADOW",
        "status": "PASS" if pass_count == len(results) and leak_count == 0 and mutation_count == 0 else "FAIL",
        "results": results,
    }
