from __future__ import annotations
import re

ROBOTIC_TERMS = ["sou a eldora", "como posso ajudar", "posso auxiliar", "compreendo", "entendo sua preocupação"]

def clamp(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

def rewrite_robotic(answer: str) -> str:
    out = str(answer or "")
    replacements = {
        "Sou a Eldora": "Sou a Eldora",
        "sou a eldora": "sou a eldora",
        "Como posso ajudar?": "Me fala o que você quer resolver.",
        "como posso ajudar": "me fala o que você quer resolver",
        "posso auxiliar": "vamos resolver",
        "compreendo": "entendi"
    }
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out.strip()

def real_humanization_runtime(user_message: str, draft_answer: str, context: dict | None = None) -> dict:
    context = context or {}
    social = context.get("social", {})
    emotion = context.get("emotion", {})
    relationship = context.get("relationship", {})

    answer = rewrite_robotic(draft_answer)
    low = answer.lower()
    user_l = str(user_message or "").lower()

    urgency = clamp(emotion.get("urgency", 0.0))
    frustration = clamp(emotion.get("frustration", 0.0))
    trust = clamp(emotion.get("trust", 0.5))

    robotic_hits = sum(1 for t in ROBOTIC_TERMS if t in low)
    robotic_probability = clamp(robotic_hits / max(len(ROBOTIC_TERMS), 1))

    continuity = 0.35
    if context.get("memory") or social.get("dominant_topics") or relationship.get("dominant_topics"):
        continuity += 0.35
    if any(x in low for x in ["contexto", "próximo passo", "progresso", "evidência", "vamos"]):
        continuity += 0.20

    cadence = "direct_single"
    if len(answer) > 450 and not any(x in answer for x in ["```", "{", "}"]):
        cadence = "structured_split"
    if urgency >= 0.7 or relationship.get("operating_mode") == "evidence_first_execution":
        cadence = "evidence_first"

    followup_probability = clamp(0.25 + (0.35 * urgency) + (0.25 * frustration) + (0.15 if "?" in user_l else 0))
    supportive_mode = frustration >= 0.45
    proactive_suitability = clamp((trust * 0.4) + (urgency * 0.3) + (continuity * 0.3))

    humanization_score = round(100 * clamp((1 - robotic_probability) * 0.45 + continuity * 0.35 + trust * 0.20), 2)

    return {
        "answer": answer,
        "messages": [answer],
        "observation": {
            "tone": relationship.get("communication_style", social.get("communication_style", "direct")),
            "urgency": urgency,
            "frustration": frustration,
            "trust": trust,
            "continuity": round(clamp(continuity), 2)
        },
        "pattern": {
            "cadence": cadence,
            "followup_probability": round(followup_probability, 2),
            "fragmentation_strategy": cadence,
            "proactive_suitability": round(proactive_suitability, 2),
            "supportive_mode": supportive_mode
        },
        "judge": {
            "humanization_score": humanization_score,
            "robotic_probability": round(robotic_probability, 2),
            "social_continuity_score": round(100 * clamp(continuity), 2),
            "rewrite_suggestions": [] if robotic_probability == 0 else ["rewrite_robotic_terms"]
        },
        "ELDORA_REAL_HUMANIZATION_ACTIVE": True
    }

