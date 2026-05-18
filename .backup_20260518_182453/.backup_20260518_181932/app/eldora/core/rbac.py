ROLE_PERMISSIONS = {
    "guest": ["read_public"],
    "user": ["read_public", "use_runtime", "memory_write"],
    "admin": ["read_public", "use_runtime", "memory_write", "manage_tenant", "apply_schema"]
}

def has_permission(role: str, permission: str):
    return permission in ROLE_PERMISSIONS.get(role, [])
