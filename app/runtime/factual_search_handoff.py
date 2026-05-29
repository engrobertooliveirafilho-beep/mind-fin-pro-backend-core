from __future__ import annotations
from app.runtime.factual_conversation_policy import apply_factual_conversation_policy
from app.runtime.factual_session_state import infer_factual_state, should_factual_search, build_factual_prompt
from app.runtime.generic_conversation_state import factual_state_allowed_for
from app.runtime.cognitive_conversation_runtime import decide_turn

_LAST_STATE={}
_RECOVERY_STEP={}

def _sender_key(inbound:str)->str:
    return "default"

def _is_factual_motorcycle_topic(raw:str)->bool:
    return any(x in raw for x in ["cr250","cr 250","250r","2001","pedal","partida","kick","kick starter","compatibilidade","comprar","preco","preço"])

def _next_deepen_step(key:str)->str:
    step=_RECOVERY_STEP.get(key,0)+1
    _RECOVERY_STEP[key]=step
    steps=[
        "Execução contextual: continuo no mesmo ponto e vou organizar o próximo teste sem resposta genérica.",
        "Execução contextual: separar o que falhou, o que testar e qual evidência registrar.",
        "Execução contextual: fechar a causa provável e avançar com validação objetiva."
    ]
    return steps[(step-1)%len(steps)]

def factual_search_handoff(answer:str,inbound:str="")->str:
    key=_sender_key(inbound)
    prev=_LAST_STATE.get(key)
    raw=(inbound or "").lower().strip()
    if not raw:
        return answer
    deepen_alias=raw in ["aprofunde","aprofundar","mais detalhes","detalhar","detalhe melhor"]
    if deepen_alias and not _is_factual_motorcycle_topic(raw):
        return _next_deepen_step(key)
    decision=decide_turn(inbound,prev)
    if not decision.allow_factual_memory and not _is_factual_motorcycle_topic(raw):
        _LAST_STATE.pop(key,None)
        return answer
    if _is_factual_motorcycle_topic(raw) and ("verifi" in raw or "quero que vc" in raw or "quero que voce" in raw or "quero que você" in raw):
        state = infer_factual_state(inbound, prev)
        _LAST_STATE[key] = state
        return "Busca factual acionada: validar compatibilidade, ano/modelo e evidência antes de recomendar a peça."

    if not _is_factual_motorcycle_topic(raw):
        return answer
    if not factual_state_allowed_for(inbound):
        return answer
    state=infer_factual_state(inbound,prev)
    if should_factual_search(state):
        _LAST_STATE[key]=state
        return apply_factual_conversation_policy(build_factual_prompt(state,inbound),inbound,key)
    return answer
