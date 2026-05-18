from app.runtime.continuity import inject_continuity_anchor
def build_response(user_message, intent, memory, internal_state, persona_context, strategy):
    base=f"Diagnóstico: entendi a intenção {intent['intent']} no contexto {internal_state.get('dominant_project','MIND')}.\nEstratégia: vou responder como Eldora, com continuidade, memória e ação concreta.\nExecução: {strategy['strategy']} sem resetar contexto e sem resposta genérica.\nAuditoria: manter persona, foco e utilidade prática."
    return inject_continuity_anchor(base, internal_state)
