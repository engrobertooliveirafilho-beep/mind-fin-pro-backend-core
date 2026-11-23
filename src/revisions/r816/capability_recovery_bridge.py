"""Passive, fail-closed inventory of historically configured capability modules.

R816: no imports, constructors, function calls, or network I/O.
"""

TOP5_MODULES = (
    "app.eldora.core.persistent_social_memory",
    "app.persona.adaptive_social_dialogue",
    "app.api.eldora_social",
    "app.retrieval.provider",
    "app.eldora.core.long_term_memory",
)


def capability_recovery_report(user_id: str = "default", message: str = "", *, execute_probes: bool = False) -> dict:
    """Return a declared-only inventory. Active probing is disabled, including opt-in.

    The report never claims a module was imported or functionally certified.
    """
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
