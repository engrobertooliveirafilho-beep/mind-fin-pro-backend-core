import inspect
from app.retrieval.semantic_provider import SemanticRetrievalProvider


def _safe_call(fn, *args):
    try:
        sig = inspect.signature(fn)
        required = [
            p for p in sig.parameters.values()
            if p.default is inspect._empty
            and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]

        argc = len(required)

        if argc == 0:
            return {"ok": True, "value": fn()}
        if argc == 1:
            return {"ok": True, "value": fn(args[0] if args else "")}
        if argc == 2:
            a = args[0] if len(args) > 0 else ""
            b = args[1] if len(args) > 1 else ""
            return {"ok": True, "value": fn(a, b)}

        return {"ok": False, "error": f"unsupported_required_argc:{argc}", "signature": str(sig)}

    except Exception as e:
        return {"ok": False, "error": type(e).__name__ + ": " + str(e)[:500]}


def capability_orchestrator(user_id: str, message: str, mode: str = "diagnostic") -> dict:
    result = {
        "orchestrator": "P4.74B_ORCHESTRATOR_DIAGNOSTIC_MODE",
        "mode": mode,
        "user_id": user_id,
        "message": message,
        "retrieval": None,
        "social": None,
        "semantic_whatsapp": None,
        "capabilities_available": [],
        "capabilities_used": [],
        "capabilities_failed": [],
        "capabilities_recommended": [],
        "status": "ok",
        "errors": [],
    }

    try:
        retriever = SemanticRetrievalProvider()
        rows = retriever.search(user_id, message, limit=5)
        result["retrieval"] = {
            "rows": len(rows),
            "items": rows[:5],
            "provider_status": retriever.status(),
        }
        result["capabilities_available"].append("semantic_retrieval")
        if rows:
            result["capabilities_used"].append("semantic_retrieval")
    except Exception as e:
        result["capabilities_failed"].append("semantic_retrieval")
        result["errors"].append({"module": "SemanticRetrievalProvider", "error": type(e).__name__ + ": " + str(e)[:500]})

    try:
        from app.api import eldora_social

        social_memory = _safe_call(eldora_social.social_memory_report)
        emotional = _safe_call(eldora_social.emotional_report)
        relational = _safe_call(eldora_social.relational_report)

        result["social"] = {
            "social_memory_report": social_memory,
            "emotional_report": emotional,
            "relational_report": relational,
        }

        result["capabilities_available"] += [
            "social_memory",
            "emotional_report",
            "relational_report",
        ]

        for name, payload in [
            ("social_memory", social_memory),
            ("emotional_report", emotional),
            ("relational_report", relational),
        ]:
            if payload.get("ok"):
                result["capabilities_used"].append(name)
            else:
                result["capabilities_failed"].append(name)

    except Exception as e:
        result["capabilities_failed"].append("eldora_social")
        result["errors"].append({"module": "app.api.eldora_social", "error": type(e).__name__ + ": " + str(e)[:500]})

    try:
        from app.runtime import semantic_whatsapp_runtime as swr

        semantic_route = _safe_call(swr.semantic_route, message)
        humanized_answer = _safe_call(swr.humanized_answer, message, message)
        ux_guard = _safe_call(swr.whatsapp_ux_guard, message)
        relationalize = _safe_call(swr.relationalize, message)

        result["semantic_whatsapp"] = {
            "semantic_route": semantic_route,
            "humanized_answer": humanized_answer,
            "whatsapp_ux_guard": ux_guard,
            "relationalize": relationalize,
        }

        result["capabilities_available"] += [
            "semantic_route",
            "humanized_answer",
            "whatsapp_ux_guard",
            "relationalize",
        ]

        for name, payload in [
            ("semantic_route", semantic_route),
            ("humanized_answer", humanized_answer),
            ("whatsapp_ux_guard", ux_guard),
            ("relationalize", relationalize),
        ]:
            if payload.get("ok"):
                result["capabilities_used"].append(name)
            else:
                result["capabilities_failed"].append(name)

    except Exception as e:
        result["capabilities_failed"].append("semantic_whatsapp_runtime")
        result["errors"].append({"module": "app.runtime.semantic_whatsapp_runtime", "error": type(e).__name__ + ": " + str(e)[:500]})

    if result["capabilities_failed"] or result["errors"]:
        result["status"] = "partial"

    if "semantic_retrieval" in result["capabilities_used"] and "social_memory" in result["capabilities_used"]:
        result["capabilities_recommended"].append("safe_to_observe_in_runtime")

    if "semantic_route" in result["capabilities_used"]:
        result["capabilities_recommended"].append("candidate_for_router_auxiliary_signal")

    return result
