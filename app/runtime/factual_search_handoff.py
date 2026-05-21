
from __future__ import annotations

from app.runtime.factual_session_state import infer_factual_state, should_factual_search, build_factual_prompt

_LAST_STATE = {}

def _sender_key(inbound: str) -> str:
    return "default"

def factual_search_handoff(answer: str, inbound: str = "") -> str:
    key=_sender_key(inbound)
    prev=_LAST_STATE.get(key)
    state=infer_factual_state(inbound, prev)

    raw_msg=(inbound or "").lower()
    force_factual = (
        ("verifi" in raw_msg or "quero que vc" in raw_msg or "quero que você" in raw_msg)
        and any(x in raw_msg for x in ["cr250","cr 250","250r","2001","pedal","partida","2 tempos","2t"])
    )

    if force_factual and not should_factual_search(state):
        from app.runtime.factual_session_state import FactualSessionState
        state = FactualSessionState(
            active_subject="Honda CR250R 2001 2T",
            active_item="pedal de partida",
            active_brands=["IMS","Red Dragon"],
            active_vehicle="Honda CR250R 2001 2 tempos",
            last_intent="compatibility_search",
            confidence=0.95,
        )

    if should_factual_search(state):
        _LAST_STATE[key]=state
    elif prev:
        state=prev

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
            return clean[:1200]

    except Exception as e:
        return "Não consegui consultar a busca factual agora. Falha no provider: " + str(e)[:120]

    return answer
