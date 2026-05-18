from app.runtime.intent_router import detect_intent
from app.runtime.internal_state import load_state
from app.runtime.response_strategy import build_strategy
from app.runtime.response_builder import build_response
from app.runtime.quality_gate import validate_response
from app.memory.memory_graph import save_message
from app.runtime.autonomous_cognition_layer import run_autonomous_cognition_layer

def run_cognitive_pipeline(user_id: str, message: str) -> dict:
    save_message(user_id, "user", message)

    intent = detect_intent(message)
    state = load_state(user_id)

    autonomous = run_autonomous_cognition_layer(user_id, message)

    strategy = build_strategy(
        intent=intent,
        state=state,
        memory=autonomous
    )

    response = build_response(
        message=message,
        intent=intent,
        state=state,
        strategy=strategy
    )

    final = validate_response(response)

    return {
        "answer": final["answer"],
        "intent": intent,
        "scores": final["scores"],
        "state": state,
        "autonomous": autonomous
    }
