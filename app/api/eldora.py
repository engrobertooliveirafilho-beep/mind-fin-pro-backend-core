from fastapi import APIRouter
from app.eldora.core.service_health_graph import service_health_graph
from app.eldora.core.startup_manager import startup_report

router = APIRouter(prefix="/eldora", tags=["eldora"])

@router.get("/health")
async def eldora_health():
    return {"status": "ok", "runtime": "eldora", "module": "omega_total_stack"}

@router.get("/modules")
async def eldora_modules():
    return {"status": "ok", "modules": "registered", "registry": "ELDORA_MODULE_REGISTRY"}

@router.get("/runtime/health-graph")
async def eldora_health_graph():
    return service_health_graph()

@router.get("/runtime/startup")
async def eldora_startup():
    return startup_report()
