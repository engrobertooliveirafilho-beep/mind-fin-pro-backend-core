from fastapi import APIRouter, Header
from app.eldora.core.jwt_auth import create_token, verify_token
from app.eldora.core.session_memory import save_session, get_session
from app.eldora.core.rate_limit_engine import check_rate_limit
router=APIRouter(prefix="/eldora/auth", tags=["eldora-auth"])
@router.post("/token")
async def token(user_id: str, tenant_id: str="default", role: str="user"): return {"status":"ok","token":create_token(user_id,tenant_id,role)}
@router.get("/verify")
async def verify(authorization: str=Header(default="")): return verify_token(authorization.replace("Bearer ","").strip())
@router.post("/session/save")
async def session_save(user_id: str, tenant_id: str="default", key: str="last_action", value: str="ok"): return save_session(user_id,tenant_id,{key:value})
@router.get("/session/get")
async def session_get(user_id: str, tenant_id: str="default"): return get_session(user_id,tenant_id)
@router.get("/rate-limit/check")
async def rate_limit(key: str="anonymous", limit: int=60): return check_rate_limit(key,limit)
