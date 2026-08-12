from __future__ import annotations

import hashlib
import json
from typing import Any

from app.runtime.p53h_self_correction_memory import (
    load_self_corrections,
)
from app.runtime.p53i_feedback_effectiveness_engine import (
    evaluate_next_user_message,
    load_effectiveness_state,
    register_correction_application,
    save_effectiveness_state,
)


def _active_correction_types(
    sender_id: str,
) -> list[str]:
    try:
        state = load_self_corrections(
            sender_id
        )
    except Exception:
        return []

    corrections = state.get(
        "corrections",
        [],
    )

    if not isinstance(corrections, list):
        return []

    result: list[str] = []

    for correction in corrections:
        if not isinstance(correction, dict):
            continue

        if correction.get("active") is not True:
            continue

        correction_type = str(
            correction.get(
                "type",
                "",
            )
            or ""
        ).strip()

        if (
            correction_type
            and correction_type not in result
        ):
            result.append(correction_type)

    return result


def _response_fingerprint(
    correction_types: list[str],
    assistant_response: str,
    subject: str,
) -> str:
    payload = {
        "correction_types": sorted(
            correction_types
        ),
        "assistant_response": str(
            assistant_response or ""
        ).strip(),
        "subject": str(
            subject or ""
        ).strip(),
    }

    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def evaluate_incoming_feedback(
    sender_id: str,
    user_message: str,
    current_subject: str = "",
) -> dict[str, Any]:
    sender = str(
        sender_id or ""
    ).strip()

    message = str(
        user_message or ""
    ).strip()

    if not sender or not message:
        return {
            "evaluated": False,
            "classification": None,
            "reason": "missing_sender_or_message",
        }

    try:
        result = evaluate_next_user_message(
            sender,
            message,
            current_subject=current_subject,
        )

        return {
            **result,
            "failed_open": False,
        }

    except Exception as error:
        return {
            "evaluated": False,
            "classification": None,
            "failed_open": True,
            "error": (
                f"{type(error).__name__}: "
                f"{str(error)[:500]}"
            ),
        }


def register_outgoing_response(
    sender_id: str,
    assistant_response: str,
    subject: str = "",
) -> dict[str, Any]:
    sender = str(
        sender_id or ""
    ).strip()

    response_text = str(
        assistant_response or ""
    ).strip()

    if not sender or not response_text:
        return {
            "registered": False,
            "deduplicated": False,
            "reason": "missing_sender_or_response",
        }

    correction_types = _active_correction_types(
        sender
    )

    if not correction_types:
        return {
            "registered": False,
            "deduplicated": False,
            "reason": "no_active_corrections",
        }

    fingerprint = _response_fingerprint(
        correction_types,
        response_text,
        subject,
    )

    try:
        existing_state = load_effectiveness_state(
            sender
        )

        pending = existing_state.get(
            "pending_evaluation"
        )

        if (
            isinstance(pending, dict)
            and pending.get("fingerprint")
            == fingerprint
        ):
            return {
                "registered": False,
                "deduplicated": True,
                "fingerprint": fingerprint,
                "correction_types": correction_types,
                "state": existing_state,
            }

        state = register_correction_application(
            sender,
            correction_types,
            response_text,
            subject=subject,
        )

        pending = state.get(
            "pending_evaluation"
        )

        if isinstance(pending, dict):
            pending["fingerprint"] = fingerprint
            pending["registration_version"] = (
                "P5.3I-B"
            )

            state["pending_evaluation"] = pending

            save_effectiveness_state(
                sender,
                state,
            )

        return {
            "registered": True,
            "deduplicated": False,
            "fingerprint": fingerprint,
            "correction_types": correction_types,
            "state": state,
        }

    except Exception as error:
        return {
            "registered": False,
            "deduplicated": False,
            "failed_open": True,
            "error": (
                f"{type(error).__name__}: "
                f"{str(error)[:500]}"
            ),
        }
