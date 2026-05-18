import uuid

from datetime import datetime, timezone

VOICE_SESSIONS = []
STREAM_EVENTS = []
PRESENCE_STATE = []

def create_voice_session(
    user_id:str,
    language:str="pt-BR"
):

    session = {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "language": language,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    VOICE_SESSIONS.append(session)

    return {
        "status":"ok",
        "session":session,
        "sessions_total":len(VOICE_SESSIONS)
    }

def stream_cognition_event(
    session_id:str,
    event:str,
    payload:str=""
):

    stream = {
        "event_id": str(uuid.uuid4()),
        "session_id": session_id,
        "event": event,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    STREAM_EVENTS.append(stream)

    return {
        "status":"ok",
        "stream":stream,
        "events_total":len(STREAM_EVENTS)
    }

def update_presence_state(
    user_id:str,
    emotion:str="neutral",
    attention:float=1.0
):

    presence = {
        "presence_id": str(uuid.uuid4()),
        "user_id": user_id,
        "emotion": emotion,
        "attention": attention,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    PRESENCE_STATE.append(presence)

    return {
        "status":"ok",
        "presence":presence
    }

def voice_runtime_report():

    return {
        "status":"ok",
        "voice_sessions":len(VOICE_SESSIONS),
        "stream_events":len(STREAM_EVENTS),
        "presence_states":len(PRESENCE_STATE),
        "sessions":VOICE_SESSIONS[-20:],
        "presence":PRESENCE_STATE[-20:]
    }
