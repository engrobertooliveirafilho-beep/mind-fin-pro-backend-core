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


_FEEDBACK_CLASSES = (
    "accepted",
    "rejected",
    "neutral",
    "topic_change",
    "implicit_acceptance",
)

_CORRECTION_TYPES = (
    "response_length",
    "format",
    "example",
    "technical_level",
    "confirmation",
    "tone",
    "general",
)


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
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def _config() -> tuple[str, str, str]:
    url = os.getenv(
        "P53I_SUPABASE_URL",
        "",
    ).strip().rstrip("/")

    key = os.getenv(
        "P53I_SUPABASE_KEY",
        "",
    ).strip()

    bucket = os.getenv(
        "P53I_SUPABASE_BUCKET",
        "mind-workspace",
    ).strip()

    if not url or not key or not bucket:
        raise RuntimeError(
            "P53I_STORAGE_NOT_CONFIGURED"
        )

    return url, key, bucket


def _object_path(sender_id: str) -> str:
    sender = str(
        sender_id or "__unknown__"
    ).strip()

    digest = hashlib.sha256(
        sender.encode("utf-8")
    ).hexdigest()

    return (
        "runtime/conversation_memory/"
        "p53i_feedback_effectiveness/"
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


def _empty_metric() -> dict[str, Any]:
    return {
        "applications": 0,
        "accepted": 0,
        "rejected": 0,
        "neutral": 0,
        "topic_change": 0,
        "implicit_acceptance": 0,
        "effectiveness_score": 0.5,
        "confidence": 0.0,
        "weight": 0.5,
        "last_success": None,
        "last_failure": None,
        "updated_at": _now(),
    }


def _default_state(
    sender_id: str,
) -> dict[str, Any]:
    return {
        "sender_id": str(
            sender_id or ""
        ).strip(),
        "pending_evaluation": None,
        "metrics": {
            correction_type: _empty_metric()
            for correction_type
            in _CORRECTION_TYPES
        },
        "feedback_events": [],
        "total_feedback_events": 0,
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


def load_effectiveness_state(
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
            "P53I_READ_FAILED_"
            f"{error.code}"
        ) from error

    if not isinstance(payload, dict):
        return _default_state(sender_id)

    default = _default_state(sender_id)
    default.update(payload)

    stored_metrics = payload.get(
        "metrics",
        {},
    )

    metrics = {}

    for correction_type in _CORRECTION_TYPES:
        metric = _empty_metric()

        if isinstance(stored_metrics, dict):
            stored = stored_metrics.get(
                correction_type,
                {},
            )

            if isinstance(stored, dict):
                metric.update(stored)

        metrics[correction_type] = metric

    default["metrics"] = metrics

    events = default.get(
        "feedback_events",
        [],
    )

    if not isinstance(events, list):
        events = []

    default["feedback_events"] = [
        event
        for event in events
        if isinstance(event, dict)
    ][-100:]

    pending = default.get(
        "pending_evaluation"
    )

    if pending is not None and not isinstance(
        pending,
        dict,
    ):
        pending = None

    default["pending_evaluation"] = pending

    return default


def save_effectiveness_state(
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
                    "P53I_WRITE_STATUS_"
                    f"{response.status}"
                )

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            "P53I_WRITE_FAILED_"
            f"{error.code}: {body[:500]}"
        ) from error


def delete_effectiveness_state(
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
            "P53I_DELETE_FAILED_"
            f"{error.code}"
        ) from error


def classify_feedback(
    user_message: str,
    previous_subject: str = "",
    current_subject: str = "",
) -> str:
    text = _normalize(user_message)
    previous = _normalize(previous_subject)
    current = _normalize(current_subject)

    rejected = (
        "nao foi isso",
        "nao e isso",
        "continua errado",
        "esta errado",
        "ta errado",
        "voce fez igual",
        "nao entendeu",
        "nao resolveu",
        "ficou pior",
        "ainda nao",
        "de novo errado",
    )

    accepted = (
        "agora sim",
        "era isso",
        "perfeito",
        "exatamente",
        "isso mesmo",
        "muito bom",
        "resolveu",
        "funcionou",
        "excelente",
        "correto",
        "show",
        "boa",
        "obrigado",
        "obrigada",
        "valeu",
    )

    topic_change = (
        "outro assunto",
        "mudar de assunto",
        "vamos falar de outra coisa",
        "agora sobre",
        "mudando de assunto",
        "outra coisa",
    )

    neutral = (
        "ok",
        "certo",
        "beleza",
        "entendi",
        "continua",
        "prossiga",
        "pode continuar",
    )

    if any(
        token in text
        for token in rejected
    ):
        return "rejected"

    if any(
        token in text
        for token in accepted
    ):
        return "accepted"

    if any(
        token in text
        for token in topic_change
    ):
        return "topic_change"

    if (
        previous
        and current
        and previous != current
    ):
        return "topic_change"

    if any(
        text == token
        or text.startswith(
            token + " "
        )
        for token in neutral
    ):
        return "neutral"

    if text:
        return "implicit_acceptance"

    return "neutral"


def _recompute_metric(
    metric: dict[str, Any],
) -> None:
    accepted = int(
        metric.get(
            "accepted",
            0,
        )
        or 0
    )

    implicit = int(
        metric.get(
            "implicit_acceptance",
            0,
        )
        or 0
    )

    rejected = int(
        metric.get(
            "rejected",
            0,
        )
        or 0
    )

    neutral = int(
        metric.get(
            "neutral",
            0,
        )
        or 0
    )

    evaluated = (
        accepted
        + implicit
        + rejected
    )

    positive_value = (
        accepted
        + (
            implicit * 0.65
        )
    )

    denominator = max(
        evaluated,
        1,
    )

    raw_score = positive_value / denominator

    sample_size = (
        evaluated
        + (
            neutral * 0.25
        )
    )

    confidence = min(
        sample_size / 10.0,
        1.0,
    )

    weighted_score = (
        0.5 * (
            1.0 - confidence
        )
        + raw_score * confidence
    )

    metric["effectiveness_score"] = round(
        raw_score,
        4,
    )

    metric["confidence"] = round(
        confidence,
        4,
    )

    metric["weight"] = round(
        max(
            0.10,
            min(
                weighted_score,
                1.0,
            ),
        ),
        4,
    )

    metric["updated_at"] = _now()


def register_correction_application(
    sender_id: str,
    correction_types: list[str] | tuple[str, ...],
    assistant_response: str,
    subject: str = "",
) -> dict[str, Any]:
    state = load_effectiveness_state(
        sender_id
    )

    valid_types = []

    for correction_type in correction_types:
        normalized = str(
            correction_type or ""
        ).strip()

        if normalized in _CORRECTION_TYPES:
            if normalized not in valid_types:
                valid_types.append(normalized)

    for correction_type in valid_types:
        metric = state["metrics"][
            correction_type
        ]

        metric["applications"] = int(
            metric.get(
                "applications",
                0,
            )
            or 0
        ) + 1

        metric["updated_at"] = _now()

    state["pending_evaluation"] = {
        "correction_types": valid_types,
        "assistant_response": str(
            assistant_response or ""
        ).strip()[:3000],
        "subject": str(
            subject or ""
        ).strip(),
        "registered_at": _now(),
    }

    save_effectiveness_state(
        sender_id,
        state,
    )

    return state


def evaluate_next_user_message(
    sender_id: str,
    user_message: str,
    current_subject: str = "",
) -> dict[str, Any]:
    state = load_effectiveness_state(
        sender_id
    )

    pending = state.get(
        "pending_evaluation"
    )

    if not isinstance(pending, dict):
        return {
            "evaluated": False,
            "classification": None,
            "state": state,
        }

    previous_subject = str(
        pending.get(
            "subject",
            "",
        )
        or ""
    )

    classification = classify_feedback(
        user_message,
        previous_subject=previous_subject,
        current_subject=current_subject,
    )

    correction_types = pending.get(
        "correction_types",
        [],
    )

    if not isinstance(
        correction_types,
        list,
    ):
        correction_types = []

    timestamp = _now()

    for correction_type in correction_types:
        if correction_type not in state["metrics"]:
            continue

        metric = state["metrics"][
            correction_type
        ]

        metric[classification] = int(
            metric.get(
                classification,
                0,
            )
            or 0
        ) + 1

        if classification in (
            "accepted",
            "implicit_acceptance",
        ):
            metric["last_success"] = timestamp

        elif classification == "rejected":
            metric["last_failure"] = timestamp

        _recompute_metric(metric)

    event = {
        "classification": classification,
        "user_message": str(
            user_message or ""
        ).strip()[:1000],
        "previous_subject": previous_subject,
        "current_subject": str(
            current_subject or ""
        ).strip(),
        "correction_types": correction_types,
        "assistant_response": str(
            pending.get(
                "assistant_response",
                "",
            )
            or ""
        )[:1000],
        "created_at": timestamp,
    }

    state["feedback_events"].append(
        event
    )

    state["feedback_events"] = (
        state["feedback_events"][-100:]
    )

    state["total_feedback_events"] = int(
        state.get(
            "total_feedback_events",
            0,
        )
        or 0
    ) + 1

    state["pending_evaluation"] = None

    save_effectiveness_state(
        sender_id,
        state,
    )

    return {
        "evaluated": True,
        "classification": classification,
        "event": event,
        "state": state,
    }


def effectiveness_prompt_context(
    state: dict[str, Any],
) -> dict[str, Any]:
    summary = {}

    metrics = state.get(
        "metrics",
        {},
    )

    if not isinstance(metrics, dict):
        metrics = {}

    for correction_type, metric in metrics.items():
        if not isinstance(metric, dict):
            continue

        applications = int(
            metric.get(
                "applications",
                0,
            )
            or 0
        )

        if applications <= 0:
            continue

        summary[correction_type] = {
            "applications": applications,
            "effectiveness_score": float(
                metric.get(
                    "effectiveness_score",
                    0.5,
                )
                or 0.5
            ),
            "confidence": float(
                metric.get(
                    "confidence",
                    0.0,
                )
                or 0.0
            ),
            "weight": float(
                metric.get(
                    "weight",
                    0.5,
                )
                or 0.5
            ),
        }

    return {
        "correction_effectiveness": summary,
        "feedback_events_count": int(
            state.get(
                "total_feedback_events",
                0,
            )
            or 0
        ),
    }
