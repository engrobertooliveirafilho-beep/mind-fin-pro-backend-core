from __future__ import annotations
from datetime import datetime, timezone

def build_relationship_profile(user_id: str, social: dict | None = None, emotion: dict | None = None, memory: dict | None = None) -> dict:
    social = social or {}
    emotion = emotion or {}
    memory = memory or {}

    topics = social.get("dominant_topics") or []
    trust = float(emotion.get("trust", 0.55))
    frustration = float(emotion.get("frustration", 0.15))
    urgency = float(emotion.get("urgency", 0.2))

    if frustration >= 0.45 or urgency >= 0.5:
        operating_mode = "evidence_first_execution"
    elif trust >= 0.75:
        operating_mode = "strategic_acceleration"
    else:
        operating_mode = "structured_guidance"

    return {
        "user_id": user_id,
        "trust_level": round(trust, 2),
        "friction_level": round(frustration, 2),
        "goal_pressure": social.get("goal_pressure", "normal"),
        "communication_style": social.get("communication_style", "direct"),
        "dominant_topics": topics,
        "operating_mode": operating_mode,
        "next_best_response_shape": "diagnostic_command_audit" if operating_mode == "evidence_first_execution" else "direct_answer",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

def relationship_profile_summary(profile: dict) -> str:
    return f"perfil_relacional: confiança={profile.get('trust_level')}; atrito={profile.get('friction_level')}; modo={profile.get('operating_mode')}; estilo={profile.get('communication_style')}"
