from typing import Dict, Any, List
from app.p17_value_proof.eldora_value_proof import run_eldora_value_proof

def create_human_review_packet() -> Dict[str, Any]:
    proof = run_eldora_value_proof()

    review_items: List[Dict[str, Any]] = []

    for item in proof["results"]:
        review_items.append({
            "id": item["id"],
            "topic": item["topic"],
            "input": item["input"],
            "baseline_score": item["baseline_score"],
            "planner_score": item["planner_score"],
            "gain_pct": item["gain_pct"],
            "human_review_required": True,
            "review_questions": [
                "A resposta com planner é mais útil que o baseline?",
                "A estrutura ficou mais clara?",
                "O plano tem etapas acionáveis?",
                "A resposta preserva o tom da Eldora?",
                "Você liberaria isso para teste interno?"
            ],
            "human_decision": "PENDING",
            "llm_judge_decision": "PENDING",
        })

    return {
        "mission": "P17B_REAL_LLM_JUDGE_OR_HUMAN_REVIEW",
        "source_mission": proof["mission"],
        "cases": len(review_items),
        "avg_gain_pct_proxy": proof["avg_gain_pct"],
        "review_mode": "HUMAN_OR_REAL_LLM_PENDING",
        "production_enabled": False,
        "runtime_modified": False,
        "real_user_sent": False,
        "auto_activation_allowed": False,
        "recommendation": "PERFORM_HUMAN_OR_REAL_LLM_REVIEW_BEFORE_PRODUCTION",
        "next_required_action": "P17C_REVIEW_DECISION_AGGREGATION",
        "status": "PASS",
        "review_items": review_items,
    }
