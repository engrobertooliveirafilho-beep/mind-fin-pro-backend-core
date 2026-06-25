from typing import Dict, Any

from app.p17_value_proof.eldora_human_review import create_human_review_packet

def aggregate_review_decision() -> Dict[str, Any]:
    packet = create_human_review_packet()

    pending = sum(
        1 for item in packet["review_items"]
        if item["human_decision"] == "PENDING" and item["llm_judge_decision"] == "PENDING"
    )

    positive_proxy = packet["avg_gain_pct_proxy"] > 15

    return {
        "mission": "P17C_REVIEW_DECISION_AGGREGATION",
        "cases": packet["cases"],
        "pending_reviews": pending,
        "avg_gain_pct_proxy": packet["avg_gain_pct_proxy"],
        "value_signal": "POSITIVE_PROXY" if positive_proxy else "WEAK_PROXY",
        "real_review_status": "PENDING" if pending > 0 else "COMPLETE",
        "production_decision": "BLOCKED_PENDING_REAL_REVIEW",
        "internal_decision": "KEEP_PLANNER_INTERNAL",
        "shadow_decision": "KEEP_RESPONSE_SHADOW_ENABLED",
        "auto_activation_allowed": False,
        "production_enabled": False,
        "runtime_modified": False,
        "real_user_sent": False,
        "next_required_action": "P17D_HUMAN_OR_REAL_LLM_REVIEW_EXECUTION",
        "status": "PASS" if positive_proxy and pending == packet["cases"] else "REVIEW",
    }
