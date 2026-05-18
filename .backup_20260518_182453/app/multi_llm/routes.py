from fastapi import APIRouter
from app.multi_llm.orchestrator import MultiLLMOrchestrator

router=APIRouter()

@router.post("/admin/multi-llm/test")
def multi_llm_test(payload:dict):
    return MultiLLMOrchestrator().route(payload.get("message",""))
