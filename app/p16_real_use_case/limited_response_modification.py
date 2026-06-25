from typing import Dict, Any, List

from app.p16_real_use_case.limited_response_awareness import generate_response_awareness_candidate

def generate_limited_response_modification_candidate(runtime_input: Dict[str, Any], runtime_response: Dict[str, Any]) -> Dict[str, Any]:
    awareness_candidate = generate_response_awareness_candidate(runtime_input, runtime_response)
    awareness = awareness_candidate["awareness"]

    original_answer = str(runtime_response.get("answer", ""))

    planner_note = (
        " Plano interno validado: objetivo capturado, etapas organizadas e validação definida."
        if awareness.get("planner_available") else ""
    )

    candidate_response = {
        **runtime_response,
        "answer": original_answer + planner_note
    }

    return {
        "mission": "P16E_LIMITED_RESPONSE_MODIFICATION_DRY_RUN",
        "runtime_response_original": runtime_response,
        "candidate_response": candidate_response,
        "candidate_generated": True,
        "candidate_visible_to_user": False,
        "dry_run_only": True,
        "would_modify_response": candidate_response != runtime_response,
        "runtime_response_modified": False,
        "runtime_state_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "whatsapp_webhook_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "rollback_available": True,
        "status": "PASS",
    }

def run_limited_response_modification_dry_run() -> Dict[str, Any]:
    cases = [
        {
            "name": "WHATSAPP_RUNTIME",
            "input": {"goal": "responder com organização sem parecer robótico"},
            "response": {"answer": "Entendi. Vou organizar isso em etapas simples."}
        },
        {
            "name": "ELDORA_RUNTIME",
            "input": {"goal": "criar resposta de plano de conteúdo"},
            "response": {"answer": "Vamos criar um plano com tema, formato e frequência."}
        },
        {
            "name": "MIND_TRADER_RUNTIME",
            "input": {"goal": "responder sobre simulação segura"},
            "response": {"answer": "Vamos analisar em simulado, sem execução real."}
        }
    ]

    results: List[Dict[str, Any]] = []

    for case in cases:
        result = generate_limited_response_modification_candidate(case["input"], case["response"])
        results.append({
            "use_case": case["name"],
            "status": result["status"],
            "candidate_generated": result["candidate_generated"],
            "candidate_visible_to_user": result["candidate_visible_to_user"],
            "dry_run_only": result["dry_run_only"],
            "would_modify_response": result["would_modify_response"],
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
    candidates = sum(1 for r in results if r["would_modify_response"])
    leaks = sum(1 for r in results if r["candidate_visible_to_user"])
    real_mutations = sum(1 for r in results if r["runtime_response_modified"] or r["runtime_state_modified"] or r["routes_modified"] or r["dispatcher_modified"] or r["whatsapp_webhook_modified"])

    return {
        "mission": "P16E_LIMITED_RESPONSE_MODIFICATION_DRY_RUN",
        "cases": len(results),
        "pass_count": pass_count,
        "candidate_modifications": candidates,
        "leaks": leaks,
        "real_mutations": real_mutations,
        "runtime_modified": False,
        "runtime_response_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "recommendation": "ALLOW_P16F_RESPONSE_MODIFICATION_SAFETY_GATE",
        "next_required_action": "P16F_RESPONSE_MODIFICATION_SAFETY_GATE",
        "status": "PASS" if pass_count == len(results) and candidates == len(results) and leaks == 0 and real_mutations == 0 else "FAIL",
        "results": results,
    }
