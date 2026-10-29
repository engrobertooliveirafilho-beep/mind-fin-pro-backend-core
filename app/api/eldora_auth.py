from fastapi import APIRouter, Header, HTTPException
from app.eldora.core.jwt_auth import verify_token
from app.eldora.core.session_memory import save_session, get_session
from app.eldora.core.rate_limit_engine import check_rate_limit

router = APIRouter(prefix="/eldora/auth", tags=["eldora-auth"])

def _claims(authorization: str):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    result = verify_token(authorization[7:].strip())
    if not result.get("valid"):
        raise HTTPException(status_code=401, detail="Invalid token")
    return result["payload"]

@router.post("/token")
async def token():
    raise HTTPException(status_code=403, detail="Unauthenticated token issuance disabled")

@router.get("/verify")
async def verify(authorization: str = Header(default="")):
    return {"valid":True, "payload":_claims(authorization)}

@router.post("/session/save")
async def session_save(user_id: str, tenant_id: str="default", key: str="last_action", value: str="ok", authorization: str=Header(default="")):
    claims = _claims(authorization)
    if user_id != claims["sub"] or tenant_id != claims["tenant_id"]:
        raise HTTPException(status_code=403, detail="Cross-tenant or cross-user access denied")
    return save_session(user_id, tenant_id, {key:value})

@router.get("/session/get")
async def session_get(user_id: str, tenant_id: str="default", authorization: str=Header(default="")):
    claims = _claims(authorization)
    if user_id != claims["sub"] or tenant_id != claims["tenant_id"]:
        raise HTTPException(status_code=403, detail="Cross-tenant or cross-user access denied")
    return get_session(user_id, tenant_id)

@router.get("/rate-limit/check")
async def rate_limit(key: str="anonymous", limit: int=60):
    return check_rate_limit(key, limit)
