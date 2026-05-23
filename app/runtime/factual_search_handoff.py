from __future__ import annotations

from app.runtime.factual_session_state import (
    infer_factual_state,
    should_factual_search,
    build_factual_prompt,
)
from app.runtime.factual_conversation_policy import apply_factual_conversation_policy

_LAST_STATE = {}
_RECOVERY_STEP = {}


def _sender_key(inbound: str) -> str:
    return "default"


def _is_eldora_or_mind_topic(raw: str) -> bool:
    return any(x in raw for x in [
        "eldora", "mind", "neura", "projeto", "lançamento",
        "lancamento", "launch", "ux", "runtime", "fluidez",
        "cac", "marketing", "sono", "dormi", "bom dia",
        "duvida", "dúvida"
    ])


def _is_factual_motorcycle_topic(raw: str) -> bool:
    return any(x in raw for x in [
        "cr250", "cr 250", "250r", "2001", "pedal", "partida",
        "2 tempos", "2t", "ims", "red dragon", "kick",
        "kick starter", "compatibilidade", "peça", "peca",
        "frete", "comprar", "preço", "preco"
    ])


def _recovery_response(key: str) -> str:
    step = _RECOVERY_STEP.get(key, 0) + 1
    _RECOVERY_STEP[key] = step

    if step == 1:
        return "Memória contextual: aprofundando o mesmo eixo sem perder continuidade."

    if step == 2:
        return "Cognição profunda: separar causa, prioridade e evidência do contexto ativo."

    return "Execução contextual: transformar o contexto ativo em ação verificável."


def factual_search_handoff(answer: str, inbound: str = "") -> str:
    key = _sender_key(inbound)
    prev = _LAST_STATE.get(key)
    raw = (inbound or "").lower().strip()

    if not raw:
        return answer

    deepen_alias = raw in [
        "aprofunde", "aprofundar", "mais detalhes",
        "detalhar", "detalhe melhor"
    ]

    if deepen_alias and not _is_factual_motorcycle_topic(raw):
        return _recovery_response(key)

    if _is_eldora_or_mind_topic(raw) and not _is_factual_motorcycle_topic(raw):
        _LAST_STATE.pop(key, None)
        return answer

    if not _is_factual_motorcycle_topic(raw):
        return answer

    force_factual = (
        ("verifi" in raw or "quero que vc" in raw or "quero que você" in raw)
        and _is_factual_motorcycle_topic(raw)
    )

    state = infer_factual_state(inbound, prev)

    if force_factual or should_factual_search(state, inbound):
        _LAST_STATE[key] = state
        prompt = build_factual_prompt(state, inbound)
        return apply_factual_conversation_policy(prompt, inbound, key)

    return answer
