import importlib
import inspect


TOP5_MODULES = [
    "app.eldora.core.persistent_social_memory",
    "app.persona.adaptive_social_dialogue",
    "app.api.eldora_social",
    "app.retrieval.provider",
    "app.eldora.core.long_term_memory",
]


def _call_by_signature(fn, user_id="default", message=""):
    if inspect.iscoroutinefunction(fn):
        return {
            "ok": False,
            "skipped": True,
            "reason": "async_function_not_called_by_sync_probe",
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
            return {"ok": True, "value": fn(user_id)}

        if argc == 2:
            return {"ok": True, "value": fn(user_id, message)}

        return {
            "ok": False,
            "error": f"unsupported_required_argc:{argc}",
            "signature": str(sig),
        }

    except Exception as e:
        return {
            "ok": False,
            "error": type(e).__name__ + ": " + str(e)[:500],
        }


def inspect_capability_module(module_name: str) -> dict:
    item = {
        "module": module_name,
        "import_ok": False,
        "functions": [],
        "classes": [],
        "call_results": {},
        "error": None,
    }

    try:
        mod = importlib.import_module(module_name)
        item["import_ok"] = True

        for name, obj in inspect.getmembers(mod):
            if name.startswith("_"):
                continue

            if inspect.isfunction(obj):
                item["functions"].append(name)

            elif inspect.isclass(obj) and obj.__module__ == module_name:
                item["classes"].append(name)

        return item

    except Exception as e:
        item["error"] = type(e).__name__ + ": " + str(e)[:500]
        return item


def capability_recovery_report(user_id: str = "default", message: str = "", *, execute_probes: bool = False) -> dict:
    """Declared-only inventory; legacy active probing is disabled even on opt-in."""
    return {
        "bridge": "P4.72D_ASYNC_SAFE_CAPABILITY_BRIDGE",
        "user_id": user_id,
        "message": message,
        "mode": "declared_only",
        "active_probe_requested": execute_probes is True,
        "active_probe_allowed": False,
        "modules": [
            {
                "module": module_name,
                "import_ok": False,
                "functions": [],
                "classes": [],
                "call_results": {},
                "skipped": True,
                "reason": "active_probe_disabled",
                "certification": "not_tested",
            }
            for module_name in TOP5_MODULES
        ],
        "summary": {
            "total": len(TOP5_MODULES),
            "import_ok": 0,
            "with_successful_calls": 0,
            "skipped_async": 0,
            "skipped_active_probes": len(TOP5_MODULES),
            "functionally_certified": 0,
        },
    }
