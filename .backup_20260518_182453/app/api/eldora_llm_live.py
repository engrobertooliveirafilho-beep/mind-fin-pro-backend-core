from fastapi import APIRouter
from app.eldora.intelligence.llm_live import generate_llm_response, select_model_by_cost

router = APIRouter(prefix="/eldora/llm-live", tags=["eldora-llm-live"])

@router.get("/health")
def health():
    return {"STATUS_FINAL": "ELDORA_LLM_LIVE_READY", "model": select_model_by_cost()}

@router.post("/respond")
def respond(payload: dict):
    out = generate_llm_response(
        prompt=payload.get("prompt", ""),
        context=payload.get("context", ""),
        intent=payload.get("intent", "general"),
    )
    return {"STATUS_FINAL": "ELDORA_LLM_LIVE_READY", **out}
