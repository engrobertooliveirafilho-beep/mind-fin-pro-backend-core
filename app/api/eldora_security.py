from fastapi import APIRouter, Header, HTTPException
from app.eldora.core.tenant_engine import resolve_tenant
from app.eldora.core.auth_context import build_auth_context
from app.eldora.core.policy_engine import evaluate_policy
from app.eldora.core.jwt_auth import verify_token

router = APIRouter(prefix="/eldora/security", tags=["eldora-security"])

def _claims(authorization: str):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    result = verify_token(authorization[7:].strip())
    if not result.get("valid"):
        raise HTTPException(status_code=401, detail="Invalid token")
    return result["payload"]

@router.get("/tenant")
async def tenant(tenant_id: str="default", authorization: str=Header(default="")):
    claims = _claims(authorization)
    if tenant_id != claims["tenant_id"]:
        raise HTTPException(status_code=403, detail="Cross-tenant access denied")
    return resolve_tenant(claims["tenant_id"])

@router.get("/auth-context")
async def auth_context(authorization: str=Header(default="")):
    _claims(authorization)
    return build_auth_context(token=authorization)

@router.get("/policy/evaluate")
async def policy(action: str="read_public", resource: str="eldora", authorization: str=Header(default="")):
    claims = _claims(authorization)
    return evaluate_policy(claims["role"], action, resource)
