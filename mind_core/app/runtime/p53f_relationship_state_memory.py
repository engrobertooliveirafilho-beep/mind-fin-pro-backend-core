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


_TONES = (
    "formal",
    "informal",
    "frustrated",
    "grateful",
    "urgent",
    "neutral",
)


def _config() -> tuple[str, str, str]:
    url = os.getenv(
        "P53F_SUPABASE_URL",
        "",
    ).strip().rstrip("/")

    key = os.getenv(
        "P53F_SUPABASE_KEY",
        "",
    ).strip()

    bucket = os.getenv(
        "P53F_SUPABASE_BUCKET",
        "mind-workspace",
    ).strip()

    if not url or not key or not bucket:
        raise RuntimeError(
            "P53F_RELATIONSHIP_STORAGE_NOT_CONFIGURED"
        )

    return url, key, bucket


def _normalize(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    text = re.sub(r"\s+", " ", text)
    return text


def detect_tone(message: str) -> str:
    text = _normalize(message)

    groups = {
        "frustrated": (
            "nao entendi",
            "nao funciona",
            "ta errado",
            "deu errado",
            "confuso",
            "complicado",
            "nao consegui",
        ),
        "grateful": (
            "obrigado",
            "obrigada",
            "valeu",
            "agradeco",
            "perfeito",
            "show",
        ),
        "urgent": (
            "urgente",
            "agora",
            "rapido",
            "o quanto antes",
            "imediatamente",
        ),
        "formal": (
            "por favor",
            "poderia",
            "gostaria",
            "agradeco",
            "senhor",
            "senhora",
        ),
        "informal": (
            "beleza",
            "blz",
            "mano",
            "cara",
            "bora",
            "fechou",
            "valeu",
        ),
    }

    for tone in (
        "frustrated",
        "grateful",
        "urgent",
        "formal",
        "informal",
    ):
        if any(
            token in text
            for token in groups[tone]
        ):
            return tone

    return "neutral"


def relationship_stage(turn_count: int) -> str:
    if turn_count <= 1:
        return "first_contact"

    if turn_count <= 5:
        return "developing"

    if turn_count <= 15:
        return "familiar"

    return "established"


def _default_state(sender_id: str) -> dict[str, Any]:
    return {
        "sender_id": str(sender_id or "").strip(),
        "turn_count": 0,
        "total_user_characters": 0,
        "average_user_message_length": 0.0,
        "tone_counts": {
            tone: 0
            for tone in _TONES
        },
        "preferred_tone": "neutral",
        "relationship_stage": "first_contact",
        "last_detected_tone": "neutral",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def _object_path(sender_id: str) -> str:
    sender = str(
        sender_id or "__unknown__"
    ).strip()

    digest = hashlib.sha256(
        sender.encode("utf-8")
    ).hexdigest()

    return (
        "runtime/conversation_memory/p53f_relationship/"
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

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return (
            "not_found" in body.lower()
            or "object not found" in body.lower()
        )

    return (
        str(payload.get("statusCode")) == "404"
        or str(payload.get("error")).lower()
        == "not_found"
        or "object not found"
        in str(payload.get("message", "")).lower()
    )


def load_relationship_state(
    sender_id: str,
) -> dict[str, Any]:
    url, key, bucket = _config()
    path = _object_path(sender_id)

    endpoint = (
        f"{url}/storage/v1/object/"
        f"{bucket}/{path}"
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
            "P53F_RELATIONSHIP_READ_FAILED_"
            f"{error.code}"
        ) from error

    if not isinstance(payload, dict):
        return _default_state(sender_id)

    default = _default_state(sender_id)
    default.update(payload)

    counts = default.get("tone_counts")

    if not isinstance(counts, dict):
        counts = {}

    default["tone_counts"] = {
        tone: int(counts.get(tone, 0) or 0)
        for tone in _TONES
    }

    return default


def save_relationship_state(
    sender_id: str,
    state: dict[str, Any],
) -> None:
    url, key, bucket = _config()
    path = _object_path(sender_id)

    endpoint = (
        f"{url}/storage/v1/object/"
        f"{bucket}/{path}"
    )

    payload = dict(state)
    payload["sender_id"] = str(
        sender_id or ""
    ).strip()

    payload["updated_at"] = datetime.now(
        timezone.utc
    ).isoformat()

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
                    "P53F_RELATIONSHIP_WRITE_STATUS_"
                    f"{response.status}"
                )

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            "P53F_RELATIONSHIP_WRITE_FAILED_"
            f"{error.code}: {body[:500]}"
        ) from error


def record_user_message(
    sender_id: str,
    message: str,
) -> dict[str, Any]:
    state = load_relationship_state(
        sender_id
    )

    tone = detect_tone(message)
    length = len(str(message or "").strip())

    state["turn_count"] = int(
        state.get("turn_count", 0) or 0
    ) + 1

    state["total_user_characters"] = int(
        state.get(
            "total_user_characters",
            0,
        ) or 0
    ) + length

    state["average_user_message_length"] = round(
        state["total_user_characters"]
        / state["turn_count"],
        2,
    )

    tone_counts = state["tone_counts"]
    tone_counts[tone] = int(
        tone_counts.get(tone, 0) or 0
    ) + 1

    state["last_detected_tone"] = tone

    state["preferred_tone"] = max(
        _TONES,
        key=lambda item: (
            tone_counts.get(item, 0),
            item == tone,
        ),
    )

    state["relationship_stage"] = (
        relationship_stage(
            state["turn_count"]
        )
    )

    save_relationship_state(
        sender_id,
        state,
    )

    return state


def delete_relationship_state(
    sender_id: str,
) -> None:
    url, key, bucket = _config()
    path = _object_path(sender_id)

    endpoint = (
        f"{url}/storage/v1/object/"
        f"{bucket}/{path}"
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
            "P53F_RELATIONSHIP_DELETE_FAILED_"
            f"{error.code}"
        ) from error


def relationship_prompt_context(
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "relationship_stage": state.get(
            "relationship_stage",
            "first_contact",
        ),
        "turn_count": int(
            state.get("turn_count", 0) or 0
        ),
        "preferred_tone": state.get(
            "preferred_tone",
            "neutral",
        ),
        "last_detected_tone": state.get(
            "last_detected_tone",
            "neutral",
        ),
        "average_user_message_length": float(
            state.get(
                "average_user_message_length",
                0,
            ) or 0
        ),
    }
