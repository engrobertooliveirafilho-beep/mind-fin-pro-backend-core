from fastapi import APIRouter
from app.eldora.core.service_health_graph import service_health_graph
from app.eldora.core.startup_manager import startup_report
from app.eldora.core.audit_ledger import audit_event, audit_report
from app.eldora.core.runtime_metrics import metrics_report
from app.eldora.core.event_bus import event_bus_report

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

@router.get("/audit/report")
async def eldora_audit_report():
    audit_event("audit_report_requested")
    return audit_report()

@router.get("/runtime/metrics")
async def eldora_metrics():
    return metrics_report()

@router.get("/runtime/events")
async def eldora_events():
    return event_bus_report()
