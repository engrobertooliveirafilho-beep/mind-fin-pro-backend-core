from app.api.eldora import router as eldora_router
from app.api.eldora_admin import router as eldora_admin_router

REGISTERED_ROUTERS = [
    eldora_router,
    eldora_admin_router
]
