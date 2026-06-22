from datetime import datetime, timezone
from typing import Any, Dict

VERSION = "P19P37B_BEHAVIOR_MODELING"

def infer_behavior_model(ctx: Dict[str, Any] | None = None, text: str = "", sender: str = "") -> Dict[str, Any]:
    ctx = dict(ctx or {})
    lower = str(text or "").lower()

    behavior = {
        "sender": sender,
        "urgency": "LOW",
        "execution_style": "UNKNOWN",
        "planning_depth": "UNKNOWN",
        "risk_tolerance": "UNKNOWN",
        "preferred_format": "UNKNOWN",
        "signals": [],
        "mode": "SHADOW_ONLY",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "version": VERSION,
    }

    if any(x in lower for x in ["prossiga", "executar", "powershell", "comando"]):
        behavior["execution_style"] = "ACTION_ORIENTED"
        behavior["preferred_format"] = "POWERSHELL"
        behavior["signals"].append("action_oriented")

    if any(x in lower for x in ["auditoria", "evidência", "snapshot", "rollback"]):
        behavior["planning_depth"] = "AUDIT_DRIVEN"
        behavior["signals"].append("audit_driven")

    if any(x in lower for x in ["rápido", "menor caminho", "máximo"]):
        behavior["urgency"] = "HIGH"
        behavior["signals"].append("speed_priority")

    if any(x in lower for x in ["seguro", "sem quebrar", "rollback"]):
        behavior["risk_tolerance"] = "CONTROLLED"
        behavior["signals"].append("safety_controlled")

    return behavior

def attach_behavior_model_shadow(ctx: Dict[str, Any] | None = None, sender: str = "", text: str = "") -> Dict[str, Any]:
    ctx = dict(ctx or {})
    ctx["p19p37b_behavior_model_shadow"] = infer_behavior_model(ctx, text=text, sender=sender)
    return ctx


def build_p19p44_behavior_modeling_evolution(
    *,
    interactions=None,
    responses=None,
    topics=None,
    engagement_events=None,
):
    """
    P19P44 Behavior Modeling Evolution.

    Shadow-only behavior layer.
    Does not mutate runtime.
    Does not mutate outbound responses.
    """

    interaction_items = list(interactions or [])
    response_items = list(responses or [])
    topic_items = list(topics or [])
    engagement_items = list(engagement_events or [])

    interaction_patterns = {
        "total_interactions": len(interaction_items),
        "short_followups": sum(
            1 for item in interaction_items
            if isinstance(item, str) and len(item.strip()) <= 20
        ),
        "question_count": sum(
            1 for item in interaction_items
            if isinstance(item, str) and "?" in item
        ),
    }

    response_preference = {
        "total_responses": len(response_items),
        "prefers_short_response": (
            bool(response_items)
            and sum(1 for item in response_items if isinstance(item, str) and len(item) <= 180)
            >= max(1, len(response_items) // 2)
        ),
        "prefers_direct_style": any(
            isinstance(item, str)
            and (
                "direto" in item.lower()
                or "sem enrolação" in item.lower()
                or "na lata" in item.lower()
            )
            for item in response_items
        ),
    }

    topic_frequency = {}
    for topic in topic_items:
        key = str(topic).strip().lower()
        if not key:
            continue
        topic_frequency[key] = topic_frequency.get(key, 0) + 1

    topic_affinity = sorted(
        topic_frequency.items(),
        key=lambda item: (-item[1], item[0]),
    )

    engagement_score = min(
        1.0,
        round(
            (
                len(interaction_items)
                + len(response_items)
                + len(topic_items)
                + len(engagement_items)
            ) / 20.0,
            4,
        ),
    )

    return {
        "program": "P19P44",
        "mode": "SHADOW_ONLY",
        "behavior_modeling_evolution": {
            "interaction_patterns": interaction_patterns,
            "response_preference": response_preference,
            "topic_affinity": topic_affinity,
            "engagement_prediction": {
                "score": engagement_score,
                "basis": {
                    "interaction_count": len(interaction_items),
                    "response_count": len(response_items),
                    "topic_count": len(topic_items),
                    "engagement_event_count": len(engagement_items),
                },
            },
        },
        "safety": {
            "runtime_mutation": False,
            "response_mutation": False,
            "rollbackable": True,
            "canary_ready": True,
        },
    }

