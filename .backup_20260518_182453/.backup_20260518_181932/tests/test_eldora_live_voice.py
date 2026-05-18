from app.eldora.core.live_voice_runtime import (
    create_voice_session,
    stream_cognition_event,
    update_presence_state
)

def test_voice_session():

    r = create_voice_session(
        "roberto"
    )

    assert r["status"] == "ok"

def test_stream_event():

    session = create_voice_session(
        "roberto"
    )

    session_id = session["session"]["session_id"]

    r = stream_cognition_event(
        session_id,
        "voice_tick"
    )

    assert r["status"] == "ok"

def test_presence_state():

    r = update_presence_state(
        "roberto",
        "focused",
        0.95
    )

    assert r["status"] == "ok"
