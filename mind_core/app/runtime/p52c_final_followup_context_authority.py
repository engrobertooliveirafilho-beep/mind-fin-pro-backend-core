from __future__ import annotations

import re
from threading import RLock
from typing import Any
from app.runtime.p52d_supabase_storage_memory import load_subject as _p52d_load_subject, save_subject as _p52d_save_subject

_LOCK = RLock()

_P53C_NON_SUBJECT_EXACT = {
    "como eu faço",
    "como faço",
    "e depois",
    "não entendi",
    "nao entendi",
    "beleza",
    "ok",
    "entendi",
    "tudo certo",
    "isso fica caro",
    "fica caro",
    "e se der problema",
    "se der problema",
}

_P53C_NON_SUBJECT_PREFIXES = (
    "explica",
    "explique",
    "simplifica",
    "resuma",
    "resume",
    "repete",
    "repita",
    "não entendi",
    "nao entendi",
    "como eu faço",
    "como faço",
    "e depois",
    "isso fica caro",
    "fica caro",
    "e se der problema",
    "se der problema",
)


def _p53c_normalize_subject(value: str) -> str:
    import re

    normalized = str(value or "").strip().lower()
    normalized = re.sub(r"[?!.,;:]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _p53c_is_valid_subject(value: str) -> bool:
    normalized = _p53c_normalize_subject(value)

    if not normalized:
        return False

    if normalized in _P53C_NON_SUBJECT_EXACT:
        return False

    if normalized.startswith(_P53C_NON_SUBJECT_PREFIXES):
        return False

    tokens = set(normalized.split())

    conversational = {
        "explica",
        "explique",
        "simples",
        "simplifica",
        "entendi",
        "depois",
        "beleza",
        "caro",
        "problema",
        "repete",
        "resuma",
    }

    domain = {
        "boi",
        "gado",
        "confinamento",
        "pecuária",
        "pecuaria",
        "automação",
        "automacao",
        "trato",
        "cocho",
        "água",
        "agua",
        "sensor",
        "sistema",
        "projeto",
        "negócio",
        "negocio",
    }

    if tokens & conversational and not tokens & domain:
        return False

    return True


_LAST_SUBJECT_BY_SENDER: dict[str, str] = {}

_FOLLOWUP_MARKERS = (
    "como eu faço",
    "como eu faco",
    "como faço",
    "como faco",
    "e depois",
    "depois",
    "qual o próximo passo",
    "qual o proximo passo",
    "continue",
    "continua",
    "explica melhor",
    "explique melhor",
)

_STOPWORDS = {
    "quero", "como", "fazer", "faço", "faco", "depois", "isso",
    "essa", "esse", "para", "com", "uma", "uns", "umas", "meu",
    "minha", "por", "que", "qual", "sobre", "mais", "melhor",
}


def _normalize(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _is_followup(text: str) -> bool:
    normalized = _normalize(text)
    if not normalized:
        return False

    words = normalized.split()
    return len(words) <= 7 and any(
        marker in normalized for marker in _FOLLOWUP_MARKERS
    )


def _clean_subject(text: str) -> str:
    normalized = _normalize(text)

    normalized = re.sub(
        r"^(quero|preciso|gostaria de|me ajuda a|me ajude a)\s+",
        "",
        normalized,
    )

    words = [
        word
        for word in re.findall(r"[a-zà-ÿ0-9_-]+", normalized)
        if word not in _STOPWORDS
    ]

    subject = " ".join(words).strip()
    return subject[:180]


def _subject_from_context(ctx: Any) -> str:
    if not isinstance(ctx, dict):
        return ""

    for key in (
        "subject",
        "topic",
        "last_subject",
        "last_topic",
        "current_subject",
        "context",
    ):
        value = ctx.get(key)
        if value and not _is_followup(str(value)):
            subject = _clean_subject(str(value))
            if subject:
                return subject

    return ""


def _remember(sender: str, body: str, ctx: Any = None) -> str:
    sender_key = str(sender or "__unknown__")

    context_subject = _subject_from_context(ctx)
    body_subject = "" if _is_followup(body) else _clean_subject(body)

    candidate = context_subject or body_subject

    if candidate and _p53c_is_valid_subject(candidate):
        _p52d_save_subject(sender_key, candidate)

        with _LOCK:
            _LAST_SUBJECT_BY_SENDER[sender_key] = candidate

        return candidate

    shared_subject = _p52d_load_subject(sender_key)

    if shared_subject:
        with _LOCK:
            _LAST_SUBJECT_BY_SENDER[sender_key] = shared_subject

        return shared_subject

    with _LOCK:
        return _LAST_SUBJECT_BY_SENDER.get(sender_key, "")


def _agro_followup(subject: str, body: str) -> str:
    inbound = _normalize(body)

    if "depois" in inbound or "próximo" in inbound or "proximo" in inbound:
        return (
            f"Depois da primeira etapa de {subject}, valide o funcionamento do trato "
            "automatizado, confira consumo por lote e corrija falhas. Em seguida, avance "
            "para monitoramento de água, pesagem, câmeras e alertas."
        )

    return (
        f"Para executar {subject}, comece pelo trato: silo com sensor de nível, "
        "balança para os ingredientes, misturador e distribuição controlada por lote. "
        "Depois integre leitura de cocho, água, pesagem e monitoramento."
    )


def _generic_followup(subject: str, body: str) -> str:
    inbound = _normalize(body)

    if "depois" in inbound or "próximo" in inbound or "proximo" in inbound:
        return (
            f"Depois de concluir a primeira etapa de {subject}, valide o resultado, "
            "corrija o que falhou e avance para a próxima ação mensurável."
        )

    return (
        f"Para fazer {subject}, transforme o objetivo em etapas, escolha a primeira "
        "ação executável, defina recursos e valide o resultado antes de avançar."
    )


def apply_final_followup_context(
    sender: str,
    body: str,
    ctx: Any,
    reply: Any,
) -> str:
    current_reply = str(reply or "")
    subject = _remember(sender, body, ctx)

    if not _is_followup(body):
        return current_reply

    if not subject:
        return current_reply

    subject_lower = subject.lower()

    if any(
        token in subject_lower
        for token in ("confinamento", "boi", "bois", "gado", "agro")
    ):
        return _agro_followup(subject, body)

    return _generic_followup(subject, body)
