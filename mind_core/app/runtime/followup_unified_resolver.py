from __future__ import annotations

import json
import re
import threading
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# P19P28K_R12_UNIVERSAL_ELLIPTICAL_CONTEXT

_STATE_FILE = (
    Path(__file__).resolve().parents[2]
    / "_runtime_state"
    / "followup_unified_state.json"
)

_LOCK = threading.RLock()


_SHORT_FOLLOWUPS = {
    "quais",
    "qual",
    "como",
    "onde",
    "quando",
    "por que",
    "porque",
    "e depois",
    "depois",
    "e agora",
    "agora",
    "prossiga",
    "continue",
    "continua",
    "detalhe",
    "detalha",
    "explique",
    "explique melhor",
    "como assim",
    "próximo",
    "proximo",
    "próximo passo",
    "proximo passo",
    "faça isso",
    "faca isso",
    "isso",
    "essas",
    "esses",
    "eles",
    "elas",
}


_ELLIPTICAL_DIRECTIVE_PATTERNS = (
    r"^(monte|crie|faça|faca|prepare|elabore|organize)\s+"
    r"(um|uma|o|a)?\s*"
    r"(plano|lista|resumo|roteiro|estratégia|estrategia|análise|analise|modelo)$",

    r"^(mostre|liste|explique|detalhe|continue|prossiga)"
    r"(\s+(isso|mais|melhor))?$",

    r"^(quais|qual|como|onde|quando|por que|porque)"
    r"(\s+(são|sao|seriam|ficam|funciona|funcionam))?$",
)


_NON_SUBSTANTIVE_TOKENS = {
    "sim",
    "não",
    "nao",
    "ok",
    "certo",
    "entendi",
    "beleza",
    "perfeito",
    "obrigado",
    "obrigada",
    "valeu",
}


def _normalize(text: Any) -> str:
    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" \t\r\n.,!?;:")
    return value


def _sender_key(sender_id: Any) -> str:
    value = str(sender_id or "").strip()
    return value or "unknown"


def _load_state() -> dict[str, dict[str, Any]]:
    if not _STATE_FILE.exists():
        return {}

    try:
        loaded = json.loads(
            _STATE_FILE.read_text(
                encoding="utf-8-sig",
            )
        )

        if not isinstance(loaded, dict):
            return {}

        result: dict[str, dict[str, Any]] = {}

        for key, value in loaded.items():
            if isinstance(value, dict):
                result[str(key)] = dict(value)

        return result
    except Exception:
        return {}


def _save_state(
    state: dict[str, dict[str, Any]],
) -> None:
    _STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = _STATE_FILE.with_suffix(
        ".json.tmp"
    )

    temporary.write_text(
        json.dumps(
            state,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary.replace(_STATE_FILE)


def _get_sender_state(
    sender_id: Any,
) -> dict[str, Any]:
    sender = _sender_key(sender_id)

    with _LOCK:
        return dict(
            _load_state().get(sender, {})
        )


def _update_sender_state(
    sender_id: Any,
    **updates: Any,
) -> dict[str, Any]:
    sender = _sender_key(sender_id)

    with _LOCK:
        all_state = _load_state()
        current = dict(
            all_state.get(sender, {})
        )

        for key, value in updates.items():
            if value is not None:
                current[key] = value

        current["updated_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

        all_state[sender] = current
        _save_state(all_state)

        return dict(current)


def is_short_followup(text: Any) -> bool:
    normalized = _normalize(text)

    if not normalized:
        return False

    if normalized in _SHORT_FOLLOWUPS:
        return True

    words = normalized.split()

    if len(words) <= 3:
        return any(
            normalized.startswith(prefix)
            for prefix in (
                "quais",
                "qual ",
                "como ",
                "onde ",
                "quando ",
                "continue",
                "prossiga",
                "detalhe",
                "explique",
            )
        )

    return False


def is_elliptical_directive(text: Any) -> bool:
    normalized = _normalize(text)

    if not normalized:
        return False

    for pattern in _ELLIPTICAL_DIRECTIVE_PATTERNS:
        if re.fullmatch(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        ):
            return True

    return False


def is_followup(text: Any) -> bool:
    return (
        is_short_followup(text)
        or is_elliptical_directive(text)
    )


def _is_substantive(text: Any) -> bool:
    normalized = _normalize(text)

    if not normalized:
        return False

    if normalized in _NON_SUBSTANTIVE_TOKENS:
        return False

    if is_followup(normalized):
        return False

    words = normalized.split()

    if len(words) >= 2:
        return True

    return len(normalized) >= 8


def resolve_followup(
    text: Any,
    context: dict[str, Any] | None = None,
) -> str | None:
    current = str(text or "").strip()
    context = dict(context or {})

    if not is_followup(current):
        return None

    active_subject = str(
        context.get("active_subject")
        or context.get("last_subject")
        or context.get("last_substantive_user_message")
        or ""
    ).strip()

    if not active_subject:
        return None

    return (
        "Assunto ativo da conversa: "
        f"{active_subject}\n"
        "Pedido atual do usuário: "
        f"{current}\n"
        "Responda ao pedido atual preservando integralmente "
        "o assunto ativo. Não peça novamente uma informação "
        "que já está expressa no assunto ativo."
    )


def expand_followup(
    text: Any,
    context: dict[str, Any] | None = None,
) -> str:
    resolved = resolve_followup(
        text,
        context,
    )

    return resolved or str(text or "").strip()


def prepare_message(
    sender_id: Any,
    message: Any,
) -> str:
    original = str(message or "").strip()

    if not original:
        return original

    sender_state = _get_sender_state(
        sender_id
    )

    if is_followup(original):
        expanded = expand_followup(
            original,
            sender_state,
        )

        _update_sender_state(
            sender_id,
            last_user_message=original,
            last_resolved_message=expanded,
            last_message_was_followup=True,
        )

        return expanded

    if _is_substantive(original):
        _update_sender_state(
            sender_id,
            active_subject=original,
            last_subject=original,
            last_substantive_user_message=original,
            last_user_message=original,
            last_resolved_message=original,
            last_message_was_followup=False,
        )

    else:
        _update_sender_state(
            sender_id,
            last_user_message=original,
            last_resolved_message=original,
            last_message_was_followup=False,
        )

    return original


def record_answer(
    sender_id: Any,
    answer: Any,
) -> None:
    value = str(answer or "").strip()

    if not value:
        return

    _update_sender_state(
        sender_id,
        last_assistant_answer=value,
    )


def get_context(
    sender_id: Any,
) -> dict[str, Any]:
    return _get_sender_state(sender_id)


def clear_context(
    sender_id: Any,
) -> None:
    sender = _sender_key(sender_id)

    with _LOCK:
        all_state = _load_state()

        if sender in all_state:
            del all_state[sender]
            _save_state(all_state)