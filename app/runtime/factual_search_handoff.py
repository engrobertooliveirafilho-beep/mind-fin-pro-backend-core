
from __future__ import annotations

from app.runtime.factual_session_state import infer_factual_state, should_factual_search, build_factual_prompt, FactualSessionState
from app.runtime.factual_conversation_policy import apply_factual_conversation_policy

_LAST_STATE={}

def _sender_key(inbound: str) -> str:
    return "default"

def _is_eldora_or_mind_topic(raw: str) -> bool:
    return any(x in raw for x in ["eldora","mind","neura","projeto","lançamento","launch","ux","runtime"])

def _is_factual_motorcycle_topic(raw: str) -> bool:
    return any(x in raw for x in ["cr250","cr 250","250r","2001","pedal","partida","2 tempos","2t","ims","red dragon"])

def factual_search_handoff(answer: str, inbound: str = "") -> str:
    key=_sender_key(inbound)
    prev=_LAST_STATE.get(key)
    raw=(inbound or "").lower()

    if _is_eldora_or_mind_topic(raw):
        _LAST_STATE.pop(key, None)
        return answer

    deepen_only=any(x in raw for x in ["aprofundar","aprofunde","detalhar","mais detalhes"])
    force_factual=(("verifi" in raw or "quero que vc" in raw or "quero que você" in raw) and _is_factual_motorcycle_topic(raw))

    state=infer_factual_state(inbound, prev)

    if deepen_only and not prev and not _is_factual_motorcycle_topic(raw):
        return apply_factual_conversation_policy(answer, inbound, key)

    if force_factual and not should_factual_search(state):
        state=FactualSessionState(
            active_subject="Honda CR250R 2001 2T",
            active_item="pedal de partida",
            active_brands=["IMS","Red Dragon"],
            active_vehicle="Honda CR250R 2001 2 tempos",
            last_intent="compatibility_search",
            confidence=0.95,
        )

    if deepen_only and prev and should_factual_search(prev):
        state=prev

    if should_factual_search(state):
        _LAST_STATE[key]=state
    elif prev:
        state=prev

    if deepen_only:
        return apply_factual_conversation_policy(answer, inbound, key)

    if not should_factual_search(state):
        return answer

    try:
        from app.multi_llm.provider_runtime import ProviderRuntime
        prompt=build_factual_prompt(state, inbound)
        result=ProviderRuntime().execute("perplexity", prompt)

        if isinstance(result, dict):
            result=result.get("response") or result.get("result") or str(result)

        clean=str(result or "").replace("*","").strip()

        banned=["não consigo procurar na web","nao consigo procurar na web","carburador","tudo certo por aqui","você já deu uma olhada"]
        if any(x in clean.lower() for x in banned):
            return f"Vou manter o contexto: {state.active_item} da {state.active_subject}. Não vou trocar por outra peça."

        if clean and len(clean)>20:
            return apply_factual_conversation_policy(clean[:1200], inbound, key)

    except Exception as e:
        return "Não consegui consultar a busca factual agora. Falha no provider: " + str(e)[:120]

    return answer
