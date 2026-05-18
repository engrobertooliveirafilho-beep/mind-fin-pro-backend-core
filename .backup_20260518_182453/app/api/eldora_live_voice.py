from fastapi import APIRouter

from app.eldora.core.live_voice_runtime import (
    create_voice_session,
    stream_cognition_event,
    update_presence_state,
    voice_runtime_report
)

router = APIRouter(
    prefix="/eldora/live-voice",
    tags=["eldora-live-voice"]
)

@router.post("/session/create")
async def create_session(
    user_id:str,
    language:str="pt-BR"
):
    return create_voice_session(
        user_id,
        language
    )

@router.post("/stream/event")
async def stream_event(
    session_id:str,
    event:str,
    payload:str=""
):
    return stream_cognition_event(
        session_id,
        event,
        payload
    )

@router.post("/presence/update")
async def update_presence(
    user_id:str,
    emotion:str="neutral",
    attention:float=1.0
):
    return update_presence_state(
        user_id,
        emotion,
        attention
    )

@router.get("/report")
async def report():
    return voice_runtime_report()
