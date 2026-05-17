from app.api.eldora import router as eldora_router
from app.api.eldora_admin import router as eldora_admin_router
from app.api.eldora_security import router as eldora_security_router
from app.api.eldora_auth import router as eldora_auth_router
from app.api.eldora_async import router as eldora_async_router
from app.api.eldora_semantic import router as eldora_semantic_router
from app.api.eldora_autonomous import router as eldora_autonomous_router
from app.api.eldora_runtime_supervisor import router as eldora_runtime_supervisor_router

REGISTERED_ROUTERS = [
    eldora_router,
    eldora_admin_router,
    eldora_security_router,
    eldora_auth_router,
    eldora_async_router,
    eldora_semantic_router,
    eldora_autonomous_router,
    eldora_runtime_supervisor_router
]





