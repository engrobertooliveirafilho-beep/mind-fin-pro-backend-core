from app.runtime.whatsapp_trace_sensor import sanitize_final_output
from app.dialogue.conversation_continuity_runtime import update,get
from app.dialogue.context_resolution_engine import resolve
from app.dialogue.generic_llm_detector import detect,rewrite
from app.dialogue.persona_consistency_guard import enforce
from app.runtime.identity_guard_runtime import guard_identity_fallback
def build_visible_response(user_text: str, focus: str = "MIND") -> str:
    # GATE1F: meta-runtime user-facing generator disabled
    return None
def visible_reformulate(
    answer: str,
    user_text: str = "",
    focus: str = "MIND"
) -> str:
    if answer and len(str(answer).strip()) > 40:
        return str(answer)
    return build_visible_response(user_text, focus)







