from fastapi import APIRouter
from app.eldora.intelligence.orchestrator import respond

router = APIRouter(prefix="/eldora/intelligence", tags=["eldora-intelligence"])

@router.post("/respond")
def intelligence_respond(payload: dict):
    out = respond(payload)
    return {"STATUS_FINAL": "ELDORA_INTELLIGENCE_ORCHESTRATOR_READY", **out}
