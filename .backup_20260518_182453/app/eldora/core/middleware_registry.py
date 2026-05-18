from app.eldora.core.feature_flags import is_enabled

REGISTERED_MIDDLEWARES = []

def register_middlewares(app):
    if not is_enabled("eldora_middleware_registry_enabled"):
        return {"enabled": False, "registered": 0}
    return {"enabled": True, "registered": len(REGISTERED_MIDDLEWARES)}
