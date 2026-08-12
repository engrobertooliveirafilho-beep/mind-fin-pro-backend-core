from __future__ import annotations

import asyncio
from contextvars import ContextVar, Token
from typing import Any
from urllib.parse import parse_qs

from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from app.runtime.p53f_relationship_state_memory import (
    record_user_message,
    relationship_prompt_context,
)

# P5.3G-B USER PREFERENCE INGRESS
from app.runtime.p53g_user_preference_memory import (
    preference_prompt_context,
    record_preference_message,
)

# P5.3H-B SELF-CORRECTION INGRESS
from app.runtime.p53h_self_correction_memory import (
    correction_prompt_context,
    record_explicit_correction,
)


_CURRENT_RELATIONSHIP_CONTEXT: ContextVar[
    dict[str, Any]
] = ContextVar(
    "p53f_current_relationship_context",
    default={},
)


def get_current_relationship_context() -> dict[str, Any]:
    return dict(
        _CURRENT_RELATIONSHIP_CONTEXT.get()
        or {}
    )


def set_current_relationship_context(
    value: dict[str, Any],
) -> Token:
    return _CURRENT_RELATIONSHIP_CONTEXT.set(
        dict(value or {})
    )


def reset_current_relationship_context(
    token: Token,
) -> None:
    _CURRENT_RELATIONSHIP_CONTEXT.reset(token)


def _decode_whatsapp_form(
    body: bytes,
    content_type: str,
) -> tuple[str, str]:
    if (
        "application/x-www-form-urlencoded"
        not in content_type.lower()
    ):
        return "", ""

    try:
        decoded = body.decode(
            "utf-8",
            errors="replace",
        )

        parsed = parse_qs(
            decoded,
            keep_blank_values=True,
        )

        sender = str(
            parsed.get("From", [""])[0]
            or ""
        ).strip()

        message = str(
            parsed.get("Body", [""])[0]
            or ""
        ).strip()

        return sender, message

    except Exception:
        return "", ""


class RelationshipIngressMiddleware(
    BaseHTTPMiddleware,
):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        token = None

        try:
            if (
                request.method.upper() == "POST"
                and request.url.path
                == "/webhook/whatsapp"
            ):
                body = await request.body()

                sender, message = _decode_whatsapp_form(
                    body,
                    request.headers.get(
                        "content-type",
                        "",
                    ),
                )

                if sender and message:
                    try:
                        state = await asyncio.to_thread(
                            record_user_message,
                            sender,
                            message,
                        )

                        context = (
                            relationship_prompt_context(
                                state
                            )
                        )

                        try:
                            preference_state = (
                                await asyncio.to_thread(
                                    record_preference_message,
                                    sender,
                                    message,
                                )
                            )

                            preference_context = (
                                preference_prompt_context(
                                    preference_state
                                )
                            )

                            context.update(
                                preference_context
                            )

                            # P5.3H-B SELF-CORRECTION INGRESS
                            try:
                                correction_state = await asyncio.to_thread(
                                    record_explicit_correction,
                                    sender,
                                    message,
                                )

                                correction_context = correction_prompt_context(
                                    correction_state
                                )

                                context.update(correction_context)

                            except Exception:
                                pass

                        except Exception:
                            pass

                        token = (
                            set_current_relationship_context(
                                context
                            )
                        )

                    except Exception:
                        # Memória de relacionamento não pode
                        # derrubar o webhook.
                        token = None

            return await call_next(request)

        finally:
            if token is not None:
                reset_current_relationship_context(
                    token
                )
