from app.eldora.core.feature_flags import is_enabled

STARTUP_TASKS = [
    "module_registry_loaded",
    "router_registry_loaded",
    "middleware_registry_loaded",
    "feature_flags_loaded"
]

def startup_report():
    return {
        "enabled": is_enabled("eldora_startup_manager_enabled"),
        "tasks": STARTUP_TASKS,
        "status": "ok"
    }

def shutdown_report():
    return {"status": "ok", "shutdown": "clean"}
