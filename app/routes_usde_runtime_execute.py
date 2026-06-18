from fastapi import APIRouter
from app.modules.usde_core.scientific_runtime_orchestrator import ScientificRuntimeOrchestrator

router = APIRouter(
    prefix="/usde/runtime",
    tags=["USDE Runtime Execution"]
)

@router.post("/execute")
def execute(payload:dict):
    return ScientificRuntimeOrchestrator().run(
        payload.get("name","runtime_execution"),
        payload.get("statement","runtime_execution")
    )
