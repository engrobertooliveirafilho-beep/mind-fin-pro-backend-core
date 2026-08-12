from __future__ import annotations

import html
import inspect
import re
from typing import Any, Callable

from app.runtime import (
    p53b_human_response_authority as _original,
)


_ACKNOWLEDGEMENTS = {
    "beleza",
    "blz",
    "ok",
    "okay",
    "certo",
    "entendi",
    "show",
    "tranquilo",
    "perfeito",
    "valeu",
    "obrigado",
    "obrigada",
    "fechou",
    "tá bom",
    "ta bom",
}

_ACK_RESPONSES = {
    "beleza": "Beleza.",
    "blz": "Beleza.",
    "ok": "Certo.",
    "okay": "Certo.",
    "certo": "Certo.",
    "entendi": "Perfeito.",
    "show": "Show.",
    "tranquilo": "Tranquilo.",
    "perfeito": "Perfeito.",
    "valeu": "Valeu.",
    "obrigado": "Por nada.",
    "obrigada": "Por nada.",
    "fechou": "Fechou.",
    "tá bom": "Certo.",
    "ta bom": "Certo.",
}

_FORBIDDEN_PATTERNS = (
    "como posso ajudar",
    "posso ajudar em algo",
    "precisa de mais alguma coisa",
    "quer saber mais",
    "tudo certo por aí",
    "tudo certo por ai",
    "vamos trabalhar isso",
    "forma prática",
    "os pontos centrais",
    "próximo passo mensurável",
    "continuando no contexto",
    "continuando no agro",
)

_EMPTY_OPENERS = (
    "claro!",
    "certamente!",
    "com certeza!",
    "sem problemas!",
)


def _normalize(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = text.strip().lower()
    text = re.sub(r"[?!.,;:]+$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _find_user_message(
    bound: inspect.BoundArguments,
) -> str:
    preferred = (
        "body",
        "message",
        "user_message",
        "incoming_message",
        "incoming_text",
        "text",
        "content",
        "prompt",
    )

    for name in preferred:
        value = bound.arguments.get(name)

        if isinstance(value, str) and value.strip():
            return _normalize(value)

    for value in bound.arguments.values():
        if isinstance(value, str) and value.strip():
            candidate = _normalize(value)

            if candidate in _ACKNOWLEDGEMENTS:
                return candidate

    return ""


def _extract_message(value: str) -> tuple[str, bool]:
    match = re.search(
        r"<Message>(.*?)</Message>",
        value,
        flags=re.DOTALL,
    )

    if not match:
        return value.strip(), False

    return html.unescape(match.group(1).strip()), True


def _replace_message(
    original: str,
    replacement: str,
    is_twiml: bool,
) -> str:
    if not is_twiml:
        return replacement

    return re.sub(
        r"(<Message>).*?(</Message>)",
        lambda match: (
            match.group(1)
            + html.escape(replacement, quote=False)
            + match.group(2)
        ),
        original,
        count=1,
        flags=re.DOTALL,
    )


def validate_response(
    user_message: str,
    response: str,
) -> str:
    incoming = _normalize(user_message)
    text, is_twiml = _extract_message(response)
    cleaned = re.sub(r"\s+", " ", text).strip()
    lowered = cleaned.lower()

    if incoming in _ACKNOWLEDGEMENTS:
        return _replace_message(
            response,
            _ACK_RESPONSES[incoming],
            is_twiml,
        )

    for opener in _EMPTY_OPENERS:
        if lowered.startswith(opener):
            cleaned = cleaned[len(opener):].strip()

    if any(
        pattern in cleaned.lower()
        for pattern in _FORBIDDEN_PATTERNS
    ):
        sentences = re.split(
            r"(?<=[.!?])\s+",
            cleaned,
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
            and not any(
                pattern in sentence.lower()
                for pattern in _FORBIDDEN_PATTERNS
            )
        ]

        cleaned = " ".join(sentences).strip()

    if not cleaned:
        cleaned = "Certo."

    if len(cleaned) > 600:
        sentences = re.split(
            r"(?<=[.!?])\s+",
            cleaned,
        )

        selected = []
        length = 0

        for sentence in sentences:
            projected = length + len(sentence) + 1

            if projected > 500:
                break

            selected.append(sentence)
            length = projected

        cleaned = " ".join(selected).strip() or cleaned[:500].strip()

    return _replace_message(
        response,
        cleaned,
        is_twiml,
    )


def _make_wrapper(
    function_name: str,
) -> Callable[..., Any]:
    original_function = getattr(
        _original,
        function_name,
    )

    signature = inspect.signature(
        original_function,
    )

    def wrapped(*args: Any, **kwargs: Any) -> Any:
        result = original_function(
            *args,
            **kwargs,
        )

        if not isinstance(result, str):
            return result

        try:
            bound = signature.bind_partial(
                *args,
                **kwargs,
            )
        except TypeError:
            return result

        user_message = _find_user_message(bound)

        if not user_message:
            return result

        return validate_response(
            user_message,
            result,
        )

    wrapped.__name__ = function_name
    wrapped.__qualname__ = function_name
    wrapped.__doc__ = original_function.__doc__
    wrapped.__signature__ = signature

    return wrapped


for _name in dir(_original):
    if _name.startswith("_"):
        continue

    _value = getattr(
        _original,
        _name,
    )

    if inspect.isfunction(_value):
        globals()[_name] = _make_wrapper(_name)
    else:
        globals()[_name] = _value


def __getattr__(name: str) -> Any:
    return getattr(_original, name)
