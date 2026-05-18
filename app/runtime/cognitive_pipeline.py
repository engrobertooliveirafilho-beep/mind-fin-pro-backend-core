def run_cognitive_pipeline(user_id: str, message: str) -> dict:
    from app.persona.eldora_core import build_persona_context
    from app.runtime.intent_router import route_intent
    from app.memory.memory_graph import save_message, retrieve_relevant_memory, retrieve_user_profile, retrieve_project_context
    from app.runtime.internal_state import update_state, persist_state
    from app.runtime.response_strategy import build_response_strategy
    from app.runtime.response_builder import build_response
    from app.runtime.quality_gate import rewrite_if_needed

    save_message(user_id, "user", message)`n    from app.runtime.autonomous_cognition_layer import run_autonomous_cognition_layer`n    autonomous = run_autonomous_cognition_layer(user_id, message)
    intent = route_intent(message)
    memory = {
        "relevant": retrieve_relevant_memory(user_id, message),
        "profile": retrieve_user_profile(user_id),
        "project": retrieve_project_context(user_id),
    }
    state = update_state(message, intent, memory)
    persona = build_persona_context(user_id, state, memory)
    strategy = build_response_strategy(intent, state, memory)
    raw = build_response(message, intent, memory, state, persona, strategy)
    final = rewrite_if_needed(raw, intent, persona, memory)
    save_message(user_id, "assistant", final["answer"])
    persist_state(user_id, state)
    return {"answer": final["answer"], "intent": intent, "scores": final["scores"], "state": state, "autonomous": autonomous}

