from fastapi import APIRouter
from app.modules.usde_core.runtime_binding import USDE_RUNTIME

router = APIRouter(prefix="/usde/runtime", tags=["USDE Runtime"])

@router.get("/status")
def runtime_status():
    return {
        "runtime_status": USDE_RUNTIME["status"],
        "module_count": len(USDE_RUNTIME["modules"]),
        "modules": USDE_RUNTIME["modules"]
    }
