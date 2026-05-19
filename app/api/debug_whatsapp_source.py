from fastapi import APIRouter
from pathlib import Path

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/whatsapp-source")
def whatsapp_source():
    p=Path("app/api/whatsapp.py")
    s=p.read_text(encoding="utf-8")
    return {
        "status":"OK",
        "has_prod_state_guard":"PROD_STATE_GUARD_DIRECT" in s,
        "has_mind_state_import":"mind_state_visible_context" in s,
        "guard_index":s.find("PROD_STATE_GUARD_DIRECT"),
        "state_import_index":s.find("mind_state_visible_context"),
        "preview":s[max(0,s.find("PROD_STATE_GUARD_DIRECT")-300):s.find("PROD_STATE_GUARD_DIRECT")+600] if "PROD_STATE_GUARD_DIRECT" in s else s[:1000]
    }
