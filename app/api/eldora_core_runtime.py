from fastapi import APIRouter, HTTPException, Header
from app.eldora.identity.service import resolve_or_create_user, export_user_data, delete_user_data
from app.eldora.consents.service import require_consent
from app.eldora.plans.service import resolve_plan, enforce_plan_limits
from app.eldora.billing.service import create_subscription, activate_premium
from app.eldora.security.service import prompt_firewall, abuse_score, block_public_admin_access

router = APIRouter(prefix="/eldora/core", tags=["eldora-core-runtime"])

@router.post("/identity/resolve")
def api_identity(payload: dict):
    return resolve_or_create_user(payload.get("phone",""), payload.get("name"))

@router.post("/consent/require")
def api_consent(payload: dict):
    return require_consent(payload)

@router.post("/plans/resolve")
def api_plan(payload: dict):
    return resolve_plan(payload.get("plan"))

@router.post("/plans/enforce")
def api_plan_limits(payload: dict):
    return enforce_plan_limits(payload.get("plan","free"), int(payload.get("usage",0)))

@router.post("/billing/subscription/create")
def api_subscription(payload: dict):
    return create_subscription(payload.get("user_id","unknown"), payload.get("plan","free"))

@router.post("/billing/premium/activate")
def api_premium(payload: dict):
    return activate_premium(payload.get("user_id","unknown"), payload.get("plan","free"))

@router.post("/lgpd/export")
def api_export(payload: dict):
    return export_user_data(payload.get("user_id","unknown"))

@router.post("/lgpd/delete")
def api_delete(payload: dict):
    return delete_user_data(payload.get("user_id","unknown"))

@router.post("/security/firewall")
def api_firewall(payload: dict):
    fw = prompt_firewall(payload.get("text",""))
    ab = abuse_score(payload.get("text",""))
    return {"firewall": fw, "abuse": ab, "allowed": not fw["blocked"] and not ab["blocked"]}

@router.get("/admin/guard")
def api_admin_guard(x_admin_token: str | None = Header(default=None)):
    gate = block_public_admin_access(x_admin_token)
    if not gate["admin_allowed"]:
        raise HTTPException(403, "admin token required")
    return gate

def p449d_usde_eldora_core_hook(*args, **kwargs):
    return {
        "ok": True,
        "hook": "p449d_usde_eldora_core_hook",
        "status": "compatibility_shim",
        "authority": "sovereign_runtime",
    }
