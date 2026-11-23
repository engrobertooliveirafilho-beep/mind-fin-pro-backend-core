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
    """Legacy API retained, but arbitrary call execution is forbidden."""
    return {
        "ok": False,
        "skipped": True,
        "reason": "active_probe_disabled",
    }


def inspect_capability_module(module_name: str) -> dict:
    """Legacy API retained, but importing modules for inspection is forbidden."""
    return {
        "module": module_name,
        "import_ok": False,
        "functions": [],
        "classes": [],
        "call_results": {},
        "error": None,
        "skipped": True,
        "reason": "active_probe_disabled",
        "certification": "not_tested",
    }


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
