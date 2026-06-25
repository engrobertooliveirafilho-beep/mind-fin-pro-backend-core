from typing import Dict, Any, List
from app.p18_conversational_execution.response_executor import execute_conversational_response
from app.p18_conversational_execution.shadow_diff import compare_runtime_vs_shadow

REAL_WHATSAPP_CASES = [
    {"user": "oi", "runtime": "Olá!"},
    {"user": "tudo bem?", "runtime": "Tudo bem!"},
    {"user": "o que vc esta achando das implementações novas?", "runtime": "As implementações novas têm gerado um impacto significativo em diversos aspectos."},
    {"user": "cite todos os aspectos significativos", "runtime": "Para abordar a solicitação de citar todos os aspectos significativos, é importante considerar diferentes áreas e contextos."},
    {"user": "prossiga", "runtime": "Para abordar o tema, é importante estruturar a resposta em etapas concretas."},
    {"user": "As implementações novas têm gerado um impacto significativo em diversos aspectos. quais são?", "runtime": "As novas implementações podem impactar significativamente em várias áreas."},
    {"user": "tenho um problema me ajuda", "runtime": "Claro! Para ajudar você de forma prática e completa, vamos seguir algumas etapas."},
    {"user": "quero o link do youtube de uma musica do metallica", "runtime": "Passo 1: Escolher a Música. Passo 2: Acessar o YouTube."},
    {"user": "quero que vc procure pra mim e me envie", "runtime": "Para que eu possa ajudá-lo de forma mais eficaz, preciso de mais informações."},
]

def run_whatsapp_real_traffic_evaluation() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    for case in REAL_WHATSAPP_CASES:
        candidate = execute_conversational_response(case["user"])
        diff = compare_runtime_vs_shadow(
            case["user"],
            {"answer": case["runtime"]},
            {"answer": candidate["answer"]}
        )

        results.append({
            "user_message": case["user"],
            "runtime_answer": case["runtime"],
            "candidate_answer": candidate["answer"],
            "runtime_score": diff["runtime_score"]["score"],
            "candidate_score": diff["candidate_score"]["score"],
            "gain": diff["gain"],
            "candidate_better": diff["candidate_better"],
            "runtime_modified": False,
            "production_enabled": False,
            "real_user_sent": False,
            "status": "PASS" if diff["candidate_better"] else "REVIEW",
        })

    better_count = sum(1 for r in results if r["candidate_better"])
    avg_gain = sum(r["gain"] for r in results) / len(results)

    return {
        "mission": "P19A_WHATSAPP_REAL_TRAFFIC_EVALUATION",
        "cases": len(results),
        "candidate_better_count": better_count,
        "avg_gain": round(avg_gain, 2),
        "runtime_modified": False,
        "production_enabled": False,
        "real_user_sent": False,
        "recommendation": "ALLOW_P19B_WHATSAPP_SHADOW_LIVE_REPLAY" if better_count >= 6 else "KEEP_INTERNAL_ONLY",
        "next_required_action": "P19B_WHATSAPP_SHADOW_LIVE_REPLAY",
        "status": "PASS" if better_count >= 6 else "REVIEW",
        "results": results,
    }
