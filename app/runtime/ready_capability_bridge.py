import inspect
import importlib


READY_MODULES = [
    "app.api.eldora_social",
    "app.admin.semantic_activation",
    "app.runtime.semantic_whatsapp_runtime",
]


SAFE_FUNCTIONS = {
    "app.api.eldora_social": [
        "social_memory_report",
        "store_social_memory",
        "emotional_report",
        "relational_report",
    ],
    "app.admin.semantic_activation": [
        "diagnose_semantic_runtime",
        "debug_context",
    ],
    "app.runtime.semantic_whatsapp_runtime": [
        "build_conversation_payload",
        "compose_human_style",
        "context_priority_reply",
        "humanized_answer",
        "relationalize",
        "semantic_route",
        "semantic_whatsapp_payload",
        "whatsapp_ux_guard",
    ],
}


def _safe_call(fn, user_id: str, message: str):
    if inspect.iscoroutinefunction(fn):
        return {
            "ok": False,
            "skipped": True,
            "reason": "async_function",
        }

    try:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())

        required = [
            p for p in params
            if p.default is inspect._empty
            and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]

        argc = len(required)

        if argc == 0:
            return {"ok": True, "value": fn()}

        if argc == 1:
            return {"ok": True, "value": fn(message)}

        if argc == 2:
            return {"ok": True, "value": fn(user_id, message)}

        return {
            "ok": False,
            "skipped": True,
            "reason": f"unsupported_required_argc:{argc}",
            "signature": str(sig),
        }

    except Exception as e:
        return {
            "ok": False,
            "error": type(e).__name__ + ": " + str(e)[:500],
        }


def ready_capability_report(user_id: str = "default", message: str = "") -> dict:
    report = {
        "bridge": "P4.73B_READY_CAPABILITY_BRIDGE",
        "user_id": user_id,
        "message": message,
        "modules": [],
    }

    for module_name in READY_MODULES:
        item = {
            "module": module_name,
            "import_ok": False,
            "functions": [],
            "safe_functions": SAFE_FUNCTIONS.get(module_name, []),
            "call_results": {},
            "error": None,
        }

        try:
            mod = importlib.import_module(module_name)
            item["import_ok"] = True

            for fname in SAFE_FUNCTIONS.get(module_name, []):
                fn = getattr(mod, fname, None)

                if not callable(fn):
                    item["call_results"][fname] = {
                        "ok": False,
                        "error": "function_not_found",
                    }
                    continue

                item["functions"].append(fname)
                item["call_results"][fname] = _safe_call(fn, user_id, message)

        except Exception as e:
            item["error"] = type(e).__name__ + ": " + str(e)[:500]

        report["modules"].append(item)

    report["summary"] = {
        "total": len(report["modules"]),
        "import_ok": len([m for m in report["modules"] if m["import_ok"]]),
        "successful_calls": sum(
            len([
                v for v in m["call_results"].values()
                if isinstance(v, dict) and v.get("ok")
            ])
            for m in report["modules"]
        ),
        "skipped_calls": sum(
            len([
                v for v in m["call_results"].values()
                if isinstance(v, dict) and v.get("skipped")
            ])
            for m in report["modules"]
        ),
    }

    return report
