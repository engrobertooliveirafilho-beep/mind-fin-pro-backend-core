from app.eldora.core.jwt_auth import verify_token

def build_auth_context(user_id: str = "anonymous", tenant_id: str = "default", role: str = "guest", token: str | None = None):
    result = verify_token(token.removeprefix("Bearer ").strip()) if token else {"valid":False}
    claims = result.get("payload", {}) if result.get("valid") else {}
    return {
        "user_id": claims.get("sub", "anonymous"),
        "tenant_id": claims.get("tenant_id", "default"),
        "role": claims.get("role", "guest"),
        "authenticated": bool(result.get("valid"))
    }
