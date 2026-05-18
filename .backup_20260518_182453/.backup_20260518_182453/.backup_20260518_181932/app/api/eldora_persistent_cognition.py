from fastapi import APIRouter
from app.eldora.core.persistent_cognitive_graph import store_persistent_memory, retrieve_persistent_memory, cognitive_store_report

router = APIRouter(prefix="/eldora/persistent-cognition", tags=["eldora-persistent-cognition"])

@router.post("/store")
async def store(content: str, tenant_id: str="default", user_ref: str="anonymous", category: str="general", priority: int=1):
    return store_persistent_memory(content, tenant_id, user_ref, category, priority)

@router.get("/retrieve")
async def retrieve(query: str, top_k: int=5):
    return retrieve_persistent_memory(query, top_k)

@router.get("/report")
async def report():
    return cognitive_store_report()
