def detect_topic_drift(message, state): return False
def recover_last_context(state): return state.get("continuity_anchor","")
def enforce_current_arc(message, state): return {"message":message,"arc":state.get("conversation_arc")}
def prevent_persona_reset(persona_context): return {**persona_context,"persona_reset_prevented":True}
def inject_continuity_anchor(response, state): return response + f"\n\nContinuidade: {state.get('continuity_anchor','Eldora/MIND')}"
