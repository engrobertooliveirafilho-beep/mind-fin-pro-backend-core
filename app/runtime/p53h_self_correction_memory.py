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


_MAX_CORRECTIONS = 50


def _config() -> tuple[str, str, str]:
    url = os.getenv(
        "P53H_SUPABASE_URL",
        "",
    ).strip().rstrip("/")

    key = os.getenv(
        "P53H_SUPABASE_KEY",
        "",
    ).strip()

    bucket = os.getenv(
        "P53H_SUPABASE_BUCKET",
        "mind-workspace",
    ).strip()

    if not url or not key or not bucket:
        raise RuntimeError(
            "P53H_CORRECTION_STORAGE_NOT_CONFIGURED"
        )

    return url, key, bucket


def _now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


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
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def _object_path(sender_id: str) -> str:
    sender = str(
        sender_id or "__unknown__"
    ).strip()

    digest = hashlib.sha256(
        sender.encode("utf-8")
    ).hexdigest()

    return (
        "runtime/conversation_memory/"
        "p53h_self_corrections/"
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
        "corrections": [],
        "corrections_recorded": 0,
        "corrections_applied": 0,
        "created_at": _now(),
        "updated_at": _now(),
    }


def _is_not_found(
    error: urllib.error.HTTPError,
) -> bool:
    body = error.read().decode(
        "utf-8",
        errors="replace",
    ).lower()

    return (
        error.code == 404
        or (
            error.code == 400
            and (
                "not_found" in body
                or "object not found" in body
                or '"statuscode":"404"' in body
            )
        )
    )


def load_self_corrections(
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
            "P53H_CORRECTION_READ_FAILED_"
            f"{error.code}"
        ) from error

    if not isinstance(payload, dict):
        return _default_state(sender_id)

    default = _default_state(sender_id)
    default.update(payload)

    corrections = default.get(
        "corrections",
        [],
    )

    if not isinstance(corrections, list):
        corrections = []

    default["corrections"] = [
        item
        for item in corrections
        if isinstance(item, dict)
    ][-_MAX_CORRECTIONS:]

    return default


def save_self_corrections(
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
                    "P53H_CORRECTION_WRITE_STATUS_"
                    f"{response.status}"
                )

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            "P53H_CORRECTION_WRITE_FAILED_"
            f"{error.code}: {body[:500]}"
        ) from error


def delete_self_corrections(
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
            "P53H_CORRECTION_DELETE_FAILED_"
            f"{error.code}"
        ) from error


def detect_explicit_correction(
    message: str,
) -> dict[str, Any] | None:
    raw = str(message or "").strip()
    text = _normalize(raw)

    markers = (
        "nao foi isso",
        "nao e isso",
        "eu quis dizer",
        "quando eu pedir",
        "da proxima vez",
        "prefiro que",
        "quero que voce",
        "nao faca mais",
        "nao use mais",
        "sempre responda",
        "corrigindo",
        "nao execute sem confirmar",
        "nao execute sem confirmacao",
        "confirme antes",
        "pergunte antes",
    )

    if not any(
        marker in text
        for marker in markers
    ):
        return None

    correction_type = "general"

    if any(
        token in text
        for token in (
            "curto",
            "duas frases",
            "resumo",
            "resuma",
            "direto",
        )
    ):
        correction_type = "response_length"

    elif any(
        token in text
        for token in (
            "lista",
            "topicos",
            "texto corrido",
        )
    ):
        correction_type = "format"

    elif any(
        token in text
        for token in (
            "exemplo",
            "exemplos",
        )
    ):
        correction_type = "example"

    elif any(
        token in text
        for token in (
            "tecnico",
            "tecnica",
            "tecnicos",
            "tecnicas",
            "simples",
            "iniciante",
            "jargao",
        )
    ):
        correction_type = "technical_level"

    elif any(
        token in text
        for token in (
            "pergunte antes",
            "confirme antes",
            "confirmar antes",
            "sem confirmar",
            "sem confirmacao",
        )
    ):
        correction_type = "confirmation"

    elif any(
        token in text
        for token in (
            "formal",
            "informal",
            "descontraido",
        )
    ):
        correction_type = "tone"

    return {
        "type": correction_type,
        "instruction": raw,
        "normalized_instruction": text,
        "created_at": _now(),
        "times_reinforced": 1,
        "active": True,
    }


def record_explicit_correction(
    sender_id: str,
    message: str,
) -> dict[str, Any]:
    state = load_self_corrections(
        sender_id
    )

    correction = detect_explicit_correction(
        message
    )

    if correction is None:
        return state

    existing = None

    for item in state["corrections"]:
        if (
            item.get("type")
            == correction["type"]
            and item.get("normalized_instruction")
            == correction[
                "normalized_instruction"
            ]
        ):
            existing = item
            break

    if existing is not None:
        existing["times_reinforced"] = int(
            existing.get(
                "times_reinforced",
                1,
            )
            or 1
        ) + 1

        existing["updated_at"] = _now()
        existing["active"] = True

    else:
        state["corrections"].append(
            correction
        )

        state["corrections"] = (
            state["corrections"][
                -_MAX_CORRECTIONS:
            ]
        )

        state["corrections_recorded"] = int(
            state.get(
                "corrections_recorded",
                0,
            )
            or 0
        ) + 1

    save_self_corrections(
        sender_id,
        state,
    )

    return state


def correction_prompt_context(
    state: dict[str, Any],
) -> dict[str, Any]:
    active = [
        item
        for item in state.get(
            "corrections",
            [],
        )
        if item.get("active") is True
    ]

    active.sort(
        key=lambda item: (
            int(
                item.get(
                    "times_reinforced",
                    1,
                )
                or 1
            ),
            str(
                item.get(
                    "created_at",
                    "",
                )
            ),
        ),
        reverse=True,
    )

    instructions = [
        str(
            item.get(
                "instruction",
                "",
            )
        ).strip()
        for item in active[:10]
        if str(
            item.get(
                "instruction",
                "",
            )
        ).strip()
    ]

    return {
        "user_explicit_corrections": instructions,
        "user_correction_count": len(
            instructions
        ),
    }


def mark_corrections_applied(
    sender_id: str,
    quantity: int = 1,
) -> dict[str, Any]:
    state = load_self_corrections(
        sender_id
    )

    state["corrections_applied"] = int(
        state.get(
            "corrections_applied",
            0,
        )
        or 0
    ) + max(
        int(quantity or 0),
        0,
    )

    save_self_corrections(
        sender_id,
        state,
    )

    return state
