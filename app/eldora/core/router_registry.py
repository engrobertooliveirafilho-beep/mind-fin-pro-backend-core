from app.api.eldora import router as eldora_router
from app.api.eldora_admin import router as eldora_admin_router
from app.api.eldora_security import router as eldora_security_router
from app.api.eldora_auth import router as eldora_auth_router
from app.api.eldora_async import router as eldora_async_router
from app.api.eldora_semantic import router as eldora_semantic_router
from app.api.eldora_autonomous import router as eldora_autonomous_router
from app.api.eldora_runtime_supervisor import router as eldora_runtime_supervisor_router
from app.api.eldora_cognition import router as eldora_cognition_router
from app.api.eldora_persistent_cognition import router as eldora_persistent_cognition_router
from app.api.eldora_multimodal import router as eldora_multimodal_router
from app.api.eldora_evolution import router as eldora_evolution_router
from app.api.eldora_swarm import router as eldora_swarm_router
from app.api.eldora_world import router as eldora_world_router
from app.api.eldora_meta import router as eldora_meta_router
from app.api.eldora_social import router as eldora_social_router
from app.api.eldora_autonomy import router as eldora_autonomy_router
from app.api.eldora_action import router as eldora_action_router
from app.api.eldora_infrastructure import router as eldora_infrastructure_router
from app.api.eldora_liveos import router as eldora_liveos_router
from app.api.eldora_mesh import router as eldora_mesh_router
from app.api.eldora_economic_market import router as eldora_economic_market_router
from app.api.eldora_embodied import router as eldora_embodied_router
from app.api.eldora_distributed import router as eldora_distributed_router
from app.api.eldora_true_distributed import router as eldora_true_distributed_router
from app.api.eldora_browser_fleet import router as eldora_browser_fleet_router
from app.api.eldora_live_voice import router as eldora_live_voice_router
from app.api.eldora_business import router as eldora_business_router
from app.api.eldora_growth import router as eldora_growth_router

REGISTERED_ROUTERS = [
    eldora_router,
    eldora_admin_router,
    eldora_security_router,
    eldora_auth_router,
    eldora_async_router,
    eldora_semantic_router,
    eldora_autonomous_router,
    eldora_runtime_supervisor_router,
    eldora_cognition_router,
    eldora_persistent_cognition_router,
    eldora_multimodal_router,
    eldora_evolution_router,
    eldora_swarm_router,
    eldora_world_router,
    eldora_meta_router,
    eldora_social_router,
    eldora_autonomy_router,
    eldora_action_router,
    eldora_infrastructure_router,
    eldora_liveos_router,
    eldora_mesh_router,
    eldora_economic_market_router,
    eldora_embodied_router,
    eldora_distributed_router,
    eldora_true_distributed_router,
    eldora_browser_fleet_router,
    eldora_live_voice_router,
    eldora_business_router,
    eldora_growth_router,
]
