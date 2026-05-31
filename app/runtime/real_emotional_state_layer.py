from __future__ import annotations
from datetime import datetime, timezone

NEGATIVE = ["erro","falha","bug","travou","ruim","não funciona","nao funciona","cansado","pressão","pressao","urgente"]
POSITIVE = ["deu certo","funcionou","melhorou","boa","ótimo","otimo","perfeito","verde"]
ACTION = ["prossiga","execute","comando","corrija","implanta","valida","teste"]

def infer_emotional_state(user_id: str, message: str, memory: dict | None = None) -> dict:
    text = (message or "").lower()
    rows = ((memory or {}).get("relevant") or {}).get("persistent_rows", []) if isinstance(memory, dict) else []
    history = " ".join(str(r.get("content","")) for r in rows).lower()
    blob = f"{history} {text}"

    frustration = min(1.0, 0.15 + 0.12 * sum(x in blob for x in NEGATIVE))
    trust = min(1.0, 0.55 + 0.10 * sum(x in blob for x in POSITIVE))
    motivation = min(1.0, 0.50 + 0.08 * sum(x in blob for x in ACTION))
    urgency = min(1.0, 0.20 + 0.20 * sum(x in blob for x in ["urgente","lançar","caixa","dinheiro","finalizar"]))

    return {
        "user_id": user_id,
        "trust": round(trust, 2),
        "frustration": round(frustration, 2),
        "motivation": round(motivation, 2),
        "urgency": round(urgency, 2),
        "recommended_tone": "direct_and_reassuring" if frustration >= 0.45 else "direct",
        "needs_progress_evidence": frustration >= 0.45 or urgency >= 0.5,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

def emotional_state_summary(state: dict) -> str:
    return f"estado_emocional: confiança={state.get('trust')}; frustração={state.get('frustration')}; urgência={state.get('urgency')}; tom={state.get('recommended_tone')}"
