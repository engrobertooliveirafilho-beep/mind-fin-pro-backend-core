from fastapi import APIRouter
from app.multi_llm.orchestrator import MultiLLMOrchestrator

router=APIRouter()

@router.post("/admin/multi-llm/live")
def multi_llm_live(payload:dict):

    message=payload.get("message","")

    return MultiLLMOrchestrator().route(message)
