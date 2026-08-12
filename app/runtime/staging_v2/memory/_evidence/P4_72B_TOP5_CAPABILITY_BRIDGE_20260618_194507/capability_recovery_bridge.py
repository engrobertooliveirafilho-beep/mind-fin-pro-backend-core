import importlib
import inspect
import json
from pathlib import Path


TOP5_MODULES = [
    "app.eldora.core.persistent_social_memory",
    "app.persona.adaptive_social_dialogue",
    "app.api.eldora_social",
    "app.retrieval.provider",
    "app.eldora.core.long_term_memory",
]


def _safe_call(fn, *args, **kwargs):
    try:
        return {
            "ok": True,
            "value": fn(*args, **kwargs),
        }
    except TypeError as e:
        return {
            "ok": False,
            "error": "TypeError: " + str(e),
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

            if inspect.isclass(obj) and obj.__module__ == module_name:
                item["classes"].append(name)

        return item

    except Exception as e:
        item["error"] = type(e).__name__ + ": " + str(e)[:500]
        return item


def capability_recovery_report(user_id: str = "default", message: str = "") -> dict:
    report = {
        "bridge": "P4.72B_TOP5_CAPABILITY_BRIDGE",
        "user_id": user_id,
        "message": message,
        "modules": [],
    }

    for module_name in TOP5_MODULES:
        item = inspect_capability_module(module_name)

        if item["import_ok"]:
            try:
                mod = importlib.import_module(module_name)

                # known safe probes
                if module_name == "app.eldora.core.persistent_social_memory":
                    if hasattr(mod, "social_memory_report"):
                        item["call_results"]["social_memory_report"] = _safe_call(
                            mod.social_memory_report,
                            user_id
                        )
                    if hasattr(mod, "store_social_memory"):
                        item["call_results"]["store_social_memory"] = _safe_call(
                            mod.store_social_memory,
                            user_id,
                            "P4.72B capability bridge probe",
                            {"source": "capability_recovery_bridge"}
                        )

                elif module_name == "app.eldora.core.long_term_memory":
                    if hasattr(mod, "retrieve_cognitive_memory"):
                        item["call_results"]["retrieve_cognitive_memory"] = _safe_call(
                            mod.retrieve_cognitive_memory,
                            user_id,
                            message or "P4.72B"
                        )

                elif module_name == "app.retrieval.provider":
                    cls = getattr(mod, "RetrievalProvider", None)
                    if cls:
                        try:
                            inst = cls()
                            item["call_results"]["RetrievalProvider_init"] = {
                                "ok": True,
                                "class": "RetrievalProvider"
                            }
                        except Exception as e:
                            item["call_results"]["RetrievalProvider_init"] = {
                                "ok": False,
                                "error": type(e).__name__ + ": " + str(e)[:500]
                            }

                elif module_name == "app.persona.adaptive_social_dialogue":
                    cls = getattr(mod, "AdaptiveSocialDialogue", None)
                    if cls:
                        try:
                            inst = cls()
                            item["call_results"]["AdaptiveSocialDialogue_init"] = {
                                "ok": True,
                                "class": "AdaptiveSocialDialogue"
                            }
                        except Exception as e:
                            item["call_results"]["AdaptiveSocialDialogue_init"] = {
                                "ok": False,
                                "error": type(e).__name__ + ": " + str(e)[:500]
                            }

            except Exception as e:
                item["probe_error"] = type(e).__name__ + ": " + str(e)[:500]

        report["modules"].append(item)

    report["summary"] = {
        "total": len(report["modules"]),
        "import_ok": len([x for x in report["modules"] if x.get("import_ok")]),
        "with_successful_calls": len([
            x for x in report["modules"]
            if any(v.get("ok") for v in x.get("call_results", {}).values() if isinstance(v, dict))
        ]),
    }

    return report
