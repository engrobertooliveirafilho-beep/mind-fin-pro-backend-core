from fastapi import APIRouter
from app.runtime.mind_state_visible_context import build_mind_state_visible_response

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/whatsapp-state-guard")
def whatsapp_state_guard():
    return {
        "status": "VISIBLE_MIND_STATE_GUARD_ACTIVE",
        "marker": "MIND_STATE_VISIBLE_CONTEXT_V1",
        "response": build_mind_state_visible_response()
    }
