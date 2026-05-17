from fastapi import APIRouter

router = APIRouter(prefix="/eldora", tags=["eldora"])

@router.get("/health")
async def eldora_health():
    return {"status": "ok", "runtime": "eldora", "module": "omega_total_stack"}

@router.get("/modules")
async def eldora_modules():
    return {"status": "ok", "modules": "registered", "registry": "ELDORA_MODULE_REGISTRY"}
