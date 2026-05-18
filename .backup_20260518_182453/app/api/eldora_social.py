from fastapi import APIRouter

from app.eldora.core.persistent_social_memory import (
    store_social_memory,
    social_memory_report
)

from app.eldora.core.emotional_continuity_engine import (
    emotional_continuity,
    emotional_report
)

from app.eldora.core.relational_cognition_engine import (
    relational_analysis,
    relational_report
)

router = APIRouter(
    prefix="/eldora/social",
    tags=["eldora-social"]
)

@router.post("/memory/store")
async def memory(user_id:str, interaction:str):
    return store_social_memory(user_id, interaction)

@router.get("/memory/report")
async def memory_runtime():
    return social_memory_report()

@router.post("/emotion/analyze")
async def emotion(user_id:str, emotion:str, context:str):
    return emotional_continuity(user_id, emotion, context)

@router.get("/emotion/report")
async def emotion_runtime():
    return emotional_report()

@router.post("/relationship/analyze")
async def relationship(user_id:str, profile:str):
    return relational_analysis(user_id, profile)

@router.get("/relationship/report")
async def relationship_runtime():
    return relational_report()
