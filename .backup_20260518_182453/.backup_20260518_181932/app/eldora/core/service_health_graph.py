from app.eldora.core.feature_flags import FEATURE_FLAGS
from app.eldora.core.module_registry import MODULE_REGISTRY
from app.eldora.core.startup_manager import startup_report

def service_health_graph():
    return {
        "runtime": "eldora",
        "status": "ok",
        "modules": MODULE_REGISTRY,
        "feature_flags": FEATURE_FLAGS,
        "startup": startup_report()
    }
