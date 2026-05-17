from fastapi import APIRouter
from app.eldora.core.tenant_engine import resolve_tenant
from app.eldora.core.auth_context import build_auth_context
from app.eldora.core.policy_engine import evaluate_policy

router = APIRouter(prefix="/eldora/security", tags=["eldora-security"])

@router.get("/tenant")
async def tenant(tenant_id: str = "default"):
    return resolve_tenant(tenant_id)

@router.get("/auth-context")
async def auth_context(user_id: str = "anonymous", tenant_id: str = "default", role: str = "guest"):
    return build_auth_context(user_id, tenant_id, role)

@router.get("/policy/evaluate")
async def policy(role: str = "guest", action: str = "read_public", resource: str = "eldora"):
    return evaluate_policy(role, action, resource)
