import os
from fastapi import Header, HTTPException

def admin_routes_enabled() -> bool:
    return os.getenv("ELDORA_ADMIN_ROUTES_ENABLED", "false").lower() == "true"

def require_admin(x_admin_token: str = Header(default="")):
    if not admin_routes_enabled():
        raise HTTPException(status_code=404, detail="not found")

    expected = os.getenv("ELDORA_ADMIN_TOKEN", "")
    if not expected or x_admin_token != expected:
        raise HTTPException(status_code=403, detail="forbidden")

    return True
