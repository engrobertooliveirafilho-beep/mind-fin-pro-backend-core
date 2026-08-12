from dataclasses import asdict
from app.runtime.capability_governance.contract import GovernanceRequest
from app.runtime.capability_governance.selector import decide, score_capability, load_index
from app.runtime.capability_governance.loader import load_shadow_capabilities

MIN_SCORE = 120

def try_knowledge_provider(text: str, context=None):
    try:
        from app.runtime.knowledge_providers.contract import build_knowledge_contract
        return {
            "ok": True,
            "provider": "build_knowledge_contract",
            "result": build_knowledge_contract(text, context or {}),
        }
    except Exception as e:
        return {
            "ok": False,
            "provider": "knowledge_provider_unavailable",
            "error": type(e).__name__ + ": " + str(e),
            "result": None,
        }

def universal_governance(text: str, context=None):
    request = GovernanceRequest(
        text=text,
        domain="universal",
        context=context or {},
    )

    decision = decide(request)
    index = load_index()
    caps = load_shadow_capabilities()

    scored = []
    for cap in caps:
        score, reasons = score_capability(cap, request, index)
        scored.append((score, cap, reasons))

    scored.sort(key=lambda x: x[0], reverse=True)

    if scored and scored[0][0] >= MIN_SCORE:
        top = scored[:5]
        return {
            "mode": "capability_selected",
            "confidence": "high",
            "top_score": top[0][0],
            "selected": [
                {
                    **asdict(cap),
                    "score": score,
                    "reasons": reasons,
                }
                for score, cap, reasons in top
            ],
            "reason": decision.reason,
        }

    kp = try_knowledge_provider(text, context)

    return {
        "mode": "knowledge_provider_fallback",
        "confidence": "low",
        "top_score": scored[0][0] if scored else None,
        "selected": [],
        "reason": "below_confidence_threshold_or_no_match",
        "knowledge_provider": kp,
    }
