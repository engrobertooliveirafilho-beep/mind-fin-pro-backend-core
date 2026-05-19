from app.runtime.whatsapp_trace_sensor import sanitize_final_output
from app.dialogue.conversation_continuity_runtime import update,get
from app.dialogue.context_resolution_engine import resolve
from app.dialogue.generic_llm_detector import detect,rewrite
from app.dialogue.persona_consistency_guard import enforce
from app.runtime.identity_guard_runtime import guard_identity_fallback
from app.runtime.continuity import inject_continuity_anchor

class ResponseBuilder:
    def __init__(self, *args, **kwargs):
        self.version = "response_builder_compat_v2"

    def build(self, user_message="", intent=None, memory=None, internal_state=None, persona_context=None, strategy=None):
        return build_response(
            user_message=user_message,
            intent=intent or {"intent":"general"},
            memory=memory or {},
            internal_state=internal_state or {},
            persona_context=persona_context or {},
            strategy=strategy or {"strategy":"responder"}
        )

    def build_response(self, *args, **kwargs):
        return self.build(*args, **kwargs)

def build_response(user_message, intent, memory, internal_state, persona_context, strategy):
    base = (
        f"Diagnóstico: entendi a intenção {intent.get('intent','general')} no contexto {internal_state.get('dominant_project','MIND')}.\n"
        f"Estratégia: vou responder como Eldora, com continuidade, memória e ação concreta.\n"
        f"Execução: {strategy.get('strategy','responder')} sem resetar contexto e sem resposta genérica.\n"
        f"Auditoria: manter persona, foco e utilidade prática."
    )
    return inject_continuity_anchor(base, internal_state)



