import importlib
import inspect


TOP5_MODULES = [
    "app.eldora.core.persistent_social_memory",
    "app.persona.adaptive_social_dialogue",
    "app.api.eldora_social",
    "app.retrieval.provider",
    "app.eldora.core.long_term_memory",
]


def _compact(value, limit=1200):
    try:
        text = str(value)
        return text[:limit]
    except Exception:
        return "<unprintable>"


def _call_by_signature(fn, user_id="default", message=""):
    try:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        argc = len([
            p for p in params
            if p.default is inspect._empty
            and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ])

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


def capability_recovery_report(user_id: str = "default", message: str = "") -> dict:
    report = {
        "bridge": "P4.72C_CAPABILITY_RECOVERY_BRIDGE",
        "user_id": user_id,
        "message": message,
        "modules": [],
    }

    for module_name in TOP5_MODULES:
        item = inspect_capability_module(module_name)

        if item["import_ok"]:
            mod = importlib.import_module(module_name)

            # Probe safe public functions
            for fname in item.get("functions", []):
                if fname.startswith("_"):
                    continue

                fn = getattr(mod, fname, None)
                if not callable(fn):
                    continue

                # avoid API route handlers with complex FastAPI context
                if module_name.startswith("app.api.") and fname not in [
                    "social_memory_report",
                    "store_social_memory",
                    "memory",
                    "memory_runtime",
                ]:
                    continue

                item["call_results"][fname] = _call_by_signature(fn, user_id, message)

            # Probe constructors
            for cname in item.get("classes", []):
                cls = getattr(mod, cname, None)
                if cls:
                    try:
                        inst = cls()
                        item["call_results"][cname + "_init"] = {
                            "ok": True,
                            "value": type(inst).__name__,
                        }
                    except Exception as e:
                        item["call_results"][cname + "_init"] = {
                            "ok": False,
                            "error": type(e).__name__ + ": " + str(e)[:500],
                        }

        report["modules"].append(item)

    report["summary"] = {
        "total": len(report["modules"]),
        "import_ok": len([x for x in report["modules"] if x.get("import_ok")]),
        "with_successful_calls": len([
            x for x in report["modules"]
            if any(v.get("ok") for v in x.get("call_results", {}).values() if isinstance(v, dict))
        ]),
        "successful_call_count": sum([
            len([
                v for v in x.get("call_results", {}).values()
                if isinstance(v, dict) and v.get("ok")
            ])
            for x in report["modules"]
        ]),
    }

    return report
