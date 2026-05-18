FEATURE_FLAGS = {
    "eldora_runtime_enabled": True,
    "eldora_middleware_registry_enabled": True,
    "eldora_startup_manager_enabled": True,
    "eldora_service_health_graph_enabled": True,
    "eldora_legacy_main_safe_mode": True
}

def is_enabled(flag: str) -> bool:
    return bool(FEATURE_FLAGS.get(flag, False))
