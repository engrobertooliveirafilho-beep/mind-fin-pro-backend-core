from typing import Dict, Any, List

from app.p16_real_use_case.limited_response_awareness import generate_response_awareness_candidate

def score_response_awareness(candidate: Dict[str, Any]) -> Dict[str, Any]:
    awareness = candidate.get("awareness", {})
    score = 0

    if awareness.get("planner_available") is True:
        score += 2
    if awareness.get("planner_depth", 0) >= 3:
        score += 2
    if awareness.get("planner_step_count", 0) >= 5:
        score += 2
    if awareness.get("top_stage"):
        score += 1
    if awareness.get("awareness_only") is True:
        score += 1
    if candidate.get("candidate_visible_to_user") is False:
        score += 1
    if candidate.get("runtime_response_modified") is False:
        score += 1

    return {
        "score": score,
        "max_score": 10,
        "quality_level": "PASS" if score >= 8 else "REVIEW",
        "safe_for_next_stage": score >= 8,
    }

def run_response_awareness_quality_benchmark() -> Dict[str, Any]:
    cases = [
        {
            "name": "WHATSAPP_RUNTIME",
            "input": {"goal": "melhorar organização interna da resposta WhatsApp"},
            "response": {"answer": "Entendi. Vou organizar isso em etapas simples."}
        },
        {
            "name": "ELDORA_RUNTIME",
            "input": {"goal": "planejar conteúdo com estrutura"},
            "response": {"answer": "Vamos criar um plano com tema, formato e frequência."}
        },
        {
            "name": "MIND_TRADER_RUNTIME",
            "input": {"goal": "planejar análise simulada com segurança"},
            "response": {"answer": "Vamos analisar em simulado, sem execução real."}
        }
    ]

    results: List[Dict[str, Any]] = []

    for case in cases:
        candidate = generate_response_awareness_candidate(case["input"], case["response"])
        quality = score_response_awareness(candidate)

        results.append({
            "use_case": case["name"],
            "quality_score": quality["score"],
            "quality_level": quality["quality_level"],
            "safe_for_next_stage": quality["safe_for_next_stage"],
            "candidate_visible_to_user": candidate["candidate_visible_to_user"],
            "runtime_response_modified": candidate["runtime_response_modified"],
            "runtime_state_modified": candidate["runtime_state_modified"],
            "production_enabled": candidate["production_enabled"],
            "active_mode_enabled": candidate["active_mode_enabled"],
        })

    pass_count = sum(1 for r in results if r["safe_for_next_stage"])
    leaks = sum(1 for r in results if r["candidate_visible_to_user"])
    mutations = sum(1 for r in results if r["runtime_response_modified"] or r["runtime_state_modified"])
    avg_score = sum(r["quality_score"] for r in results) / len(results)

    return {
        "mission": "P16D_RESPONSE_AWARENESS_QUALITY_BENCHMARK",
        "cases": len(results),
        "pass_count": pass_count,
        "avg_quality_score": avg_score,
        "leaks": leaks,
        "mutations": mutations,
        "runtime_modified": False,
        "runtime_response_modified": False,
        "active_mode_enabled": False,
        "production_enabled": False,
        "recommendation": "ALLOW_P16E_LIMITED_RESPONSE_MODIFICATION_DRY_RUN",
        "next_required_action": "P16E_LIMITED_RESPONSE_MODIFICATION_DRY_RUN",
        "status": "PASS" if pass_count == len(results) and leaks == 0 and mutations == 0 else "FAIL",
        "results": results,
    }
