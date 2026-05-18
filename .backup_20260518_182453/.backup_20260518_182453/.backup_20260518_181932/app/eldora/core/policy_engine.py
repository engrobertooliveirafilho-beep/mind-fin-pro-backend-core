from app.eldora.core.rbac import has_permission

def evaluate_policy(role: str, action: str, resource: str = "eldora"):
    allowed = has_permission(role, action)
    return {
        "status": "ok",
        "allowed": allowed,
        "role": role,
        "action": action,
        "resource": resource
    }
