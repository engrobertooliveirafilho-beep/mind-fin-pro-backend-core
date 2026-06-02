# P4_28E_RUNTIME_FUSION_IMPORTS
try:
    from app.runtime.semantic_answer_engine import answer_semantically as _p428e_semantic_answer
except Exception:
    _p428e_semantic_answer = None
try:
    from app.runtime.decision_memory import recall_decision_context as _p428e_recall_decision
except Exception:
    _p428e_recall_decision = None
try:
    from app.runtime.real_humanization_runtime import humanize_response as _p428e_humanize
except Exception:
    _p428e_humanize = None
try:
    from app.runtime.universal_conversation_os import process_universal_conversation as _p428e_universal
except Exception:
    _p428e_universal = None
try:
    from app.runtime.live_whatsapp_response import build_live_whatsapp_response as _p428e_whatsapp_live
except Exception:
    _p428e_whatsapp_live = None
# /P4_28E_RUNTIME_FUSION_IMPORTS

from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
def run_cognitive_pipeline(user_id: str, message: str) -> dict:
    from app.persona.eldora_core import build_persona_context
    from app.runtime.intent_router import route_intent
    from app.memory.memory_graph import save_message, retrieve_relevant_memory, retrieve_user_profile, retrieve_project_context
    from app.runtime.internal_state import update_state, persist_state
    from app.runtime.response_strategy import build_response_strategy
    from app.runtime.response_builder import build_response
    from app.runtime.quality_gate import rewrite_if_needed
    from app.runtime.autonomous_cognition_layer import run_autonomous_cognition_layer
    from app.runtime.natural_response_layer import naturalize_response
    from app.runtime.real_social_memory_layer import infer_social_profile
    from app.runtime.real_emotional_state_layer import infer_emotional_state
    from app.runtime.real_relationship_profile_layer import build_relationship_profile

    save_message(user_id, "user", message)

    msg_l = (message or "").lower().strip()

    if any(x in msg_l for x in ["tudo bem", "como ta", "como tá", "ta bem", "tá bem"]):
        return {"answer": "Está funcionando bem, de forma natural. E com você?", "intent": "smalltalk"}
        save_message(user_id, "assistant", answer)
        return {
            "answer": answer,
            "intent": {"intent": "smalltalk"},
            "scores": {},
            "state": {},
            "autonomous": {}
        }

    # =====================================================
    # HARD OVERRIDE — GREETINGS
    # =====================================================

    if "boa tarde" in msg_l:
        answer = "Boa tarde, Roberto. Estou aqui e acompanhando o contexto da conversa."
        save_message(user_id, "assistant", answer)
        return {
            "answer": answer,
            "intent": {"intent": "greeting"},
            "scores": {},
            "state": {},
            "autonomous": {}
        }

    if "bom dia" in msg_l:
        answer = "Bom dia, Roberto. Estou acompanhando o contexto e pronta para continuar."
        save_message(user_id, "assistant", answer)
        return {
            "answer": answer,
            "intent": {"intent": "greeting"},
            "scores": {},
            "state": {},
            "autonomous": {}
        }

    if "boa noite" in msg_l:
        answer = "Boa noite, Roberto. O contexto do MIND continua ativo."
        save_message(user_id, "assistant", answer)
        return {
            "answer": answer,
            "intent": {"intent": "greeting"},
            "scores": {},
            "state": {},
            "autonomous": {}
        }
    if any(x in msg_l for x in [
        "cade a resposta",
        "cadê a resposta",
        "onde ta a resposta",
        "onde está a resposta"
    ]):
        answer = "Roberto, resposta direta: o problema atual não é infraestrutura. É continuidade conversacional."
        save_message(user_id, "assistant", answer)
        return {
            "answer": answer,
            "intent": {"intent": "where_answer"},
            "scores": {},
            "state": {},
            "autonomous": {}
        }
    intent = route_intent(message)
    autonomous = run_autonomous_cognition_layer(user_id, message)

    memory = {
        "relevant": retrieve_relevant_memory(user_id, message),
        "profile": retrieve_user_profile(user_id),
        "project": retrieve_project_context(user_id),
        "autonomous": autonomous
    }

    # P4_16D_REAL_SOCIAL_LAYERS_ACTIVE
    social = infer_social_profile(user_id, message, memory)
    emotion = infer_emotional_state(user_id, message, memory)
    relationship = build_relationship_profile(user_id, social, emotion, memory)
    memory["social"] = social
    memory["emotion"] = emotion
    memory["relationship"] = relationship

    state = update_state(message, intent, memory)
    persona = build_persona_context(user_id, state, memory)
    strategy = build_response_strategy(intent, state, memory)

    raw = build_response(message, intent, memory, state, persona, strategy)
    final = rewrite_if_needed(raw, intent, persona, memory)
    final["answer"] = naturalize_response(final["answer"], intent, state, autonomous)

    save_message(user_id, "assistant", final["answer"])
    persist_state(user_id, state)

    return {
        "answer": final["answer"],
        "intent": intent,
        "scores": final["scores"],
        "state": state,
        "autonomous": autonomous,
        "social": memory.get("social", {}),
        "emotion": memory.get("emotion", {}),
        "relationship": memory.get("relationship", {})
    }






# FINAL_IDENTITY_BLOCK
def __identity_guard_last_hop(answer,user_message=""):
    return enforce_no_identity_in_normal_chat(user_message,answer)


# P4_28E_RUNTIME_FUSION_ADAPTER
def _p428e_runtime_fusion(user_text: str, base_answer: str = "", sender_id: str = "unknown", context: dict | None = None) -> str:
    context = context or {}
    answer = base_answer or ""

    try:
        if _p428e_recall_decision:
            context["decision_memory"] = _p428e_recall_decision(sender_id=sender_id, text=user_text)
    except Exception:
        pass

    try:
        if _p428e_humanize and answer:
            h = _p428e_humanize(answer, context=context)
            if h and isinstance(h,str):
                answer = h
    except Exception:
        pass

    return answer or base_answer or ""# /P4_28E_RUNTIME_FUSION_ADAPTER




