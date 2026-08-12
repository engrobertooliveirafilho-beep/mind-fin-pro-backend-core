from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


_PREFERENCE_KEYS = (
    "response_length",
    "list_preference",
    "technical_level",
    "formality",
    "example_preference",
    "step_by_step",
    "confirmation_preference",
)


_DEFAULT_PREFERENCES = {
    "response_length": "balanced",
    "list_preference": "neutral",
    "technical_level": "general",
    "formality": "neutral",
    "example_preference": "neutral",
    "step_by_step": "neutral",
    "confirmation_preference": "neutral",
}


def _config() -> tuple[str, str, str]:
    url = os.getenv(
        "P53G_SUPABASE_URL",
        "",
    ).strip().rstrip("/")

    key = os.getenv(
        "P53G_SUPABASE_KEY",
        "",
    ).strip()

    bucket = os.getenv(
        "P53G_SUPABASE_BUCKET",
        "mind-workspace",
    ).strip()

    if not url or not key or not bucket:
        raise RuntimeError(
            "P53G_PREFERENCE_STORAGE_NOT_CONFIGURED"
        )

    return url, key, bucket


def _normalize(value: Any) -> str:
    text = str(value or "").strip().lower()

    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def _now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _object_path(sender_id: str) -> str:
    sender = str(
        sender_id or "__unknown__"
    ).strip()

    digest = hashlib.sha256(
        sender.encode("utf-8")
    ).hexdigest()

    return (
        "runtime/conversation_memory/"
        "p53g_user_preferences/"
        f"{digest}.json"
    )


def _headers(
    key: str,
    content_type: str | None = None,
) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {key}",
        "apikey": key,
    }

    if content_type:
        headers["Content-Type"] = content_type

    return headers


def _default_state(
    sender_id: str,
) -> dict[str, Any]:
    return {
        "sender_id": str(
            sender_id or ""
        ).strip(),
        "preferences": dict(
            _DEFAULT_PREFERENCES
        ),
        "evidence": {
            key: {}
            for key in _PREFERENCE_KEYS
        },
        "messages_analyzed": 0,
        "explicit_preferences": 0,
        "created_at": _now(),
        "updated_at": _now(),
    }


def _is_not_found(
    error: urllib.error.HTTPError,
) -> bool:
    body = error.read().decode(
        "utf-8",
        errors="replace",
    )

    if error.code == 404:
        return True

    if error.code != 400:
        return False

    lowered = body.lower()

    return (
        "not_found" in lowered
        or "object not found" in lowered
        or '"statuscode":"404"' in lowered
    )


def load_user_preferences(
    sender_id: str,
) -> dict[str, Any]:
    url, key, bucket = _config()

    endpoint = (
        f"{url}/storage/v1/object/"
        f"{bucket}/{_object_path(sender_id)}"
    )

    request = urllib.request.Request(
        endpoint,
        headers=_headers(key),
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=30,
        ) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        if _is_not_found(error):
            return _default_state(sender_id)

        raise RuntimeError(
            "P53G_PREFERENCE_READ_FAILED_"
            f"{error.code}"
        ) from error

    if not isinstance(payload, dict):
        return _default_state(sender_id)

    default = _default_state(sender_id)
    default.update(payload)

    preferences = payload.get(
        "preferences",
        {},
    )

    evidence = payload.get(
        "evidence",
        {},
    )

    default["preferences"] = {
        **_DEFAULT_PREFERENCES,
        **(
            preferences
            if isinstance(preferences, dict)
            else {}
        ),
    }

    default["evidence"] = {
        key: (
            evidence.get(key, {})
            if isinstance(evidence, dict)
            else {}
        )
        for key in _PREFERENCE_KEYS
    }

    return default


def save_user_preferences(
    sender_id: str,
    state: dict[str, Any],
) -> None:
    url, key, bucket = _config()

    endpoint = (
        f"{url}/storage/v1/object/"
        f"{bucket}/{_object_path(sender_id)}"
    )

    payload = dict(state)
    payload["sender_id"] = str(
        sender_id or ""
    ).strip()
    payload["updated_at"] = _now()

    data = json.dumps(
        payload,
        ensure_ascii=False,
    ).encode("utf-8")

    headers = _headers(
        key,
        "application/json",
    )
    headers["x-upsert"] = "true"

    request = urllib.request.Request(
        endpoint,
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=30,
        ) as response:
            if response.status not in (200, 201):
                raise RuntimeError(
                    "P53G_PREFERENCE_WRITE_STATUS_"
                    f"{response.status}"
                )

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            "P53G_PREFERENCE_WRITE_FAILED_"
            f"{error.code}: {body[:500]}"
        ) from error


def delete_user_preferences(
    sender_id: str,
) -> None:
    url, key, bucket = _config()

    endpoint = (
        f"{url}/storage/v1/object/"
        f"{bucket}/{_object_path(sender_id)}"
    )

    request = urllib.request.Request(
        endpoint,
        headers=_headers(key),
        method="DELETE",
    )

    try:
        urllib.request.urlopen(
            request,
            timeout=30,
        ).close()

    except urllib.error.HTTPError as error:
        if _is_not_found(error):
            return

        raise RuntimeError(
            "P53G_PREFERENCE_DELETE_FAILED_"
            f"{error.code}"
        ) from error


def _contains_any(
    text: str,
    phrases: tuple[str, ...],
) -> bool:
    return any(
        phrase in text
        for phrase in phrases
    )


def _signals(
    message: str,
) -> list[tuple[str, str, bool]]:
    text = _normalize(message)
    detected: dict[
        str,
        tuple[str, bool],
    ] = {}

    # Negação tem precedência absoluta.
    if _contains_any(
        text,
        (
            "sem lista",
            "nao use lista",
            "nao quero lista",
            "evite lista",
            "texto corrido",
        ),
    ):
        detected["list_preference"] = (
            "avoid",
            True,
        )

    elif _contains_any(
        text,
        (
            "em lista",
            "use lista",
            "quero lista",
            "por topicos",
            "em topicos",
        ),
    ):
        detected["list_preference"] = (
            "prefer",
            True,
        )

    if _contains_any(
        text,
        (
            "sem passo a passo",
            "nao precisa detalhar etapas",
            "nao use etapas",
        ),
    ):
        detected["step_by_step"] = (
            "avoid",
            True,
        )

    elif _contains_any(
        text,
        (
            "passo a passo",
            "por etapas",
            "um passo de cada vez",
        ),
    ):
        detected["step_by_step"] = (
            "prefer",
            True,
        )

    if _contains_any(
        text,
        (
            "sem exemplo",
            "nao precisa de exemplo",
            "nao use exemplo",
        ),
    ):
        detected["example_preference"] = (
            "avoid",
            True,
        )

    elif _contains_any(
        text,
        (
            "de um exemplo",
            "com exemplo",
            "use exemplos",
            "mostre um exemplo",
        ),
    ):
        detected["example_preference"] = (
            "prefer",
            True,
        )

    if _contains_any(
        text,
        (
            "nao pergunte",
            "pode executar direto",
            "sem pedir confirmacao",
            "nao precisa confirmar",
        ),
    ):
        detected[
            "confirmation_preference"
        ] = (
            "avoid",
            True,
        )

    elif _contains_any(
        text,
        (
            "confirme antes",
            "confirmar antes",
            "pergunte antes",
            "nao execute sem confirmar",
            "peca confirmacao",
        ),
    ):
        detected[
            "confirmation_preference"
        ] = (
            "require",
            True,
        )

    if _contains_any(
        text,
        (
            "resposta curta",
            "responda curto",
            "seja direto",
            "direto ao ponto",
            "sem enrolacao",
            "resuma",
            "mais curto",
        ),
    ):
        detected["response_length"] = (
            "short",
            True,
        )

    elif _contains_any(
        text,
        (
            "explique detalhado",
            "mais detalhes",
            "aprofunde",
            "explicacao completa",
            "quero entender tudo",
        ),
    ):
        detected["response_length"] = (
            "detailed",
            True,
        )

    if _contains_any(
        text,
        (
            "mais simples",
            "linguagem simples",
            "como se eu fosse iniciante",
            "sem termos tecnicos",
        ),
    ):
        detected["technical_level"] = (
            "simple",
            True,
        )

    elif _contains_any(
        text,
        (
            "pode ser tecnico",
            "pode usar linguagem tecnica",
            "linguagem tecnica",
            "detalhes tecnicos",
            "nivel avancado",
        ),
    ):
        detected["technical_level"] = (
            "advanced",
            True,
        )

    if _contains_any(
        text,
        (
            "sem formalidade",
            "fala normal",
            "pode falar informal",
            "pode ser descontraido",
        ),
    ):
        detected["formality"] = (
            "informal",
            True,
        )

    elif _contains_any(
        text,
        (
            "seja formal",
            "linguagem profissional",
            "tom profissional",
        ),
    ):
        detected["formality"] = (
            "formal",
            True,
        )

    return [
        (
            key,
            value,
            explicit,
        )
        for key, (
            value,
            explicit,
        ) in detected.items()
    ]


def record_preference_message(
    sender_id: str,
    message: str,
) -> dict[str, Any]:
    state = load_user_preferences(
        sender_id
    )

    state["messages_analyzed"] = int(
        state.get(
            "messages_analyzed",
            0,
        ) or 0
    ) + 1

    preferences = state["preferences"]
    evidence = state["evidence"]

    signals = _signals(message)

    for key, value, explicit in signals:
        bucket = evidence.setdefault(
            key,
            {},
        )

        bucket[value] = int(
            bucket.get(value, 0)
            or 0
        ) + (
            3
            if explicit
            else 1
        )

        preferences[key] = max(
            bucket,
            key=lambda item: (
                bucket[item],
                item == value,
            ),
        )

        if explicit:
            state[
                "explicit_preferences"
            ] = int(
                state.get(
                    "explicit_preferences",
                    0,
                ) or 0
            ) + 1

    save_user_preferences(
        sender_id,
        state,
    )

    return state


def preference_prompt_context(
    state: dict[str, Any],
) -> dict[str, Any]:
    preferences = state.get(
        "preferences",
        {},
    )

    return {
        "user_response_length": preferences.get(
            "response_length",
            "balanced",
        ),
        "user_list_preference": preferences.get(
            "list_preference",
            "neutral",
        ),
        "user_technical_level": preferences.get(
            "technical_level",
            "general",
        ),
        "user_formality": preferences.get(
            "formality",
            "neutral",
        ),
        "user_example_preference": preferences.get(
            "example_preference",
            "neutral",
        ),
        "user_step_by_step": preferences.get(
            "step_by_step",
            "neutral",
        ),
        "user_confirmation_preference": preferences.get(
            "confirmation_preference",
            "neutral",
        ),
    }
