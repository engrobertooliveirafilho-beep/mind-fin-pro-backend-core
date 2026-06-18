from fastapi import APIRouter
from app.modules.usde_core.scientific_runtime_orchestrator import ScientificRuntimeOrchestrator

router = APIRouter(
    prefix="/usde/science",
    tags=["USDE Science"]
)

@router.post("/run")
def run_scientific_hypothesis(payload:dict):
    return ScientificRuntimeOrchestrator().run(
        payload.get("name","unnamed"),
        payload.get("statement","no_statement")
    )
