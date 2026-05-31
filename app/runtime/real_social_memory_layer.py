from __future__ import annotations
from datetime import datetime, timezone
import re

def infer_social_profile(user_id: str, message: str, memory: dict | None = None) -> dict:
    text = (message or "").lower()
    rows = ((memory or {}).get("relevant") or {}).get("persistent_rows", []) if isinstance(memory, dict) else []
    history = " ".join(str(r.get("content","")) for r in rows).lower()

    topics = []
    for key in ["mind","eldora","whatsapp","render","supabase","marketing","lançamento","runtime","memória","drive"]:
        if key in text or key in history:
            topics.append(key)

    pressure = "high" if any(x in text for x in ["urgente","lançar","caixa","dinheiro","finalizar","travado","erro","falha"]) else "normal"
    style = "direct_execution" if any(x in text for x in ["comando","powershell","prossiga","execute","direto"]) else "strategic"

    return {
        "user_id": user_id,
        "dominant_topics": sorted(set(topics))[:12],
        "communication_style": style,
        "goal_pressure": pressure,
        "interaction_patterns": {
            "asks_for_execution": any(x in text for x in ["prossiga","execute","comando","powershell"]),
            "launch_oriented": any(x in text for x in ["lançar","vender","caixa","assinatura","free","paga"]),
            "debug_oriented": any(x in text for x in ["erro","falha","teste","pytest","runtime","commit"])
        },
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

def social_memory_summary(profile: dict) -> str:
    topics = ", ".join(profile.get("dominant_topics") or []) or "sem tópico dominante"
    return f"perfil_social: estilo={profile.get('communication_style')}; pressão={profile.get('goal_pressure')}; tópicos={topics}"
