def build_auth_context(user_id: str = "anonymous", tenant_id: str = "default", role: str = "guest"):
    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "authenticated": user_id != "anonymous"
    }
