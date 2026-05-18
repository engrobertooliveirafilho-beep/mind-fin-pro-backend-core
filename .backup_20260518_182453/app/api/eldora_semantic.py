from fastapi import APIRouter
from app.eldora.core.semantic_memory_engine import (
    store_memory,
    retrieve_memory,
    semantic_graph_report
)

router = APIRouter(prefix="/eldora/semantic", tags=["eldora-semantic"])

@router.post("/memory/store")
async def memory_store(text: str, node: str = "default"):
    return store_memory(text, {"node": node})

@router.get("/memory/retrieve")
async def memory_retrieve(query: str, top_k: int = 3):
    return retrieve_memory(query, top_k)

@router.get("/graph")
async def graph():
    return semantic_graph_report()
