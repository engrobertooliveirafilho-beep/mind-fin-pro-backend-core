from fastapi import APIRouter

from app.eldora.core.long_term_memory import (
    store_cognitive_memory,
    retrieve_cognitive_memory
)

from app.eldora.core.memory_compression_engine import (
    compress_memory,
    compression_report
)

from app.eldora.core.tool_learning_engine import (
    learn_tool,
    tool_report
)

router = APIRouter(prefix="/eldora/cognition", tags=["eldora-cognition"])

@router.post("/memory/store")
async def cognitive_store(content: str, category: str = "general"):
    return store_cognitive_memory(content, category)

@router.get("/memory/report")
async def cognitive_report():
    return retrieve_cognitive_memory()

@router.post("/compression/run")
async def compression(content: str):
    return compress_memory(content)

@router.get("/compression/report")
async def compression_runtime():
    return compression_report()

@router.post("/tool/learn")
async def tool_learn(tool_name: str, capability: str):
    return learn_tool(tool_name, capability)

@router.get("/tool/report")
async def tools():
    return tool_report()
