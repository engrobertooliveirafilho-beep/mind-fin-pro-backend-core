from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Optional


def _config() -> tuple[str, str, str]:
    url = os.getenv("P52D_SUPABASE_URL", "").strip().rstrip("/")
    key = os.getenv("P52D_SUPABASE_KEY", "").strip()
    bucket = os.getenv(
        "P52D_SUPABASE_BUCKET",
        "mind-workspace",
    ).strip()

    if not url or not key or not bucket:
        raise RuntimeError("P52D_SUPABASE_STORAGE_NOT_CONFIGURED")

    return url, key, bucket


def _object_path(sender_id: str) -> str:
    sender = str(sender_id or "__unknown__").strip()
    digest = hashlib.sha256(sender.encode("utf-8")).hexdigest()

    return (
        "runtime/conversation_memory/p52d/"
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


def _is_not_found(error: urllib.error.HTTPError) -> bool:
    body = error.read().decode("utf-8", errors="replace")

    if error.code == 404:
        return True

    if error.code != 400:
        return False

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return '"404"' in body and "not_found" in body.lower()

    return (
        str(payload.get("statusCode")) == "404"
        or str(payload.get("error")).lower() == "not_found"
        or "object not found" in str(
            payload.get("message", "")
        ).lower()
    )


def save_subject(sender_id: str, subject: str) -> None:
    value = str(subject or "").strip()

    if not value:
        return

    url, key, bucket = _config()
    path = _object_path(sender_id)

    payload = json.dumps(
        {
            "subject": value,
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        ensure_ascii=False,
    ).encode("utf-8")

    endpoint = (
        f"{url}/storage/v1/object/"
        f"{bucket}/{path}"
    )

    headers = _headers(
        key,
        "application/json",
    )
    headers["x-upsert"] = "true"

    request = urllib.request.Request(
        endpoint,
        data=payload,
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
                    "P52D_STORAGE_WRITE_STATUS_"
                    f"{response.status}"
                )

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            "P52D_STORAGE_WRITE_FAILED_"
            f"{error.code}: {body[:500]}"
        ) from error


def load_subject(sender_id: str) -> Optional[str]:
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
                response.read().decode(
                    "utf-8",
                    errors="strict",
                )
            )

    except urllib.error.HTTPError as error:
        if _is_not_found(error):
            return None

        raise RuntimeError(
            "P52D_STORAGE_READ_FAILED_"
            f"{error.code}"
        ) from error

    subject = str(
        payload.get("subject") or ""
    ).strip()

    return subject or None


def delete_subject(sender_id: str) -> None:
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
            "P52D_STORAGE_DELETE_FAILED_"
            f"{error.code}"
        ) from error
