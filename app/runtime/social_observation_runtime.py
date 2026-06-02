
import re
from typing import Dict, Any

GENERIC_PATTERNS = [
    "próximo passo objetivo",
    "definir entrada",
    "validar saída",
    "registrar evidência",
    "qual item exato",
    "não entendi",
    "reformule"
]

def observe_social_reply(user_msg: str, reply: str, context: dict | None = None) -> Dict[str, Any]:
    user=(user_msg or "").strip()
    ans=(reply or "").strip()
    low=ans.lower()

    generic_hits=[p for p in GENERIC_PATTERNS if p in low]
    question = "?" in user
    multiline = "\n" in ans
    too_long = len(ans) > 420
    too_short = len(ans) < 8

    robotic_risk = min(1.0, (len(generic_hits)*0.28) + (0.15 if too_short else 0) + (0.12 if too_long else 0))
    social_continuity = max(0.0, 1.0 - robotic_risk)

    if any(x in user.lower() for x in ["oi","bom dia","boa noite","tudo bem"]):
        intent="social"
    elif question:
        intent="question"
    elif any(x in user.lower() for x in ["prossiga","execute","rode","corrija"]):
        intent="execution"
    else:
        intent="general"

    suggested_shape = "burst" if too_long or multiline else "single"
    cadence = "short_natural" if intent=="social" else "direct_operational"

    return {
        "ok": True,
        "intent": intent,
        "robotic_risk": round(robotic_risk,4),
        "social_continuity": round(social_continuity,4),
        "generic_hits": generic_hits,
        "suggested_shape": suggested_shape,
        "cadence": cadence,
        "multi_message_ready": suggested_shape == "burst",
        "needs_rewrite": robotic_risk >= 0.28,
    }

def social_rewrite_if_needed(user_msg: str, reply: str, context: dict | None = None) -> str:
    obs=observe_social_reply(user_msg, reply, context)
    if not obs["needs_rewrite"]:
        return reply
    low=(reply or "").lower()
    if "qual item exato" in low:
        return "Me manda o ponto exato e eu valido direto."
    if "próximo passo objetivo" in low:
        return "Vamos pelo próximo passo real: validar a entrada, testar a saída e registrar prova."
    if "não entendi" in low or "reformule" in low:
        return "Não pegou claro. Manda em uma frase que eu resolvo direto."
    return reply
