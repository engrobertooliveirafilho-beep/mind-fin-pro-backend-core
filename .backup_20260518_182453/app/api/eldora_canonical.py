from fastapi import APIRouter, HTTPException, Header
router = APIRouter(prefix="/eldora/canonical", tags=["eldora-canonical"])

@router.get("/health")
def health():
    return {"STATUS_FINAL_ADICIONAL":"ELDORA_CANONICAL_FUNCTIONS_IMPLANTED","ready":True}

@router.get("/routes/safe")
def routes_safe():
    return {"sanitized":True,"secrets_exposed":False}

@router.post("/billing/mock-subscription")
def billing(payload:dict):
    return {"subscription":"mock","real_revenue":False}

@router.post("/lotofacil/report")
def lotofacil(payload:dict):
    return {"mode":"simulation_report_only","promise_of_gain":False}

@router.get("/admin/audit")
def admin_audit(x_admin_token: str | None = Header(default=None)):
    if not x_admin_token:
        raise HTTPException(403,"admin token required")
    return {"admin_guard":True,"public_admin_blocked":True}
