from __future__ import annotations

import re
from urllib.parse import parse_qs

from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from app.runtime.p53i_runtime_feedback_bridge import (
    evaluate_incoming_feedback,
    register_outgoing_response,
)


def _decode_whatsapp_form(
    body: bytes,
    content_type: str,
) -> tuple[str, str]:
    if (
        "application/x-www-form-urlencoded"
        not in str(content_type or "").lower()
    ):
        return "", ""

    try:
        parsed = parse_qs(
            body.decode(
                "utf-8",
                errors="replace",
            ),
            keep_blank_values=True,
        )

        sender = str(
            parsed.get(
                "From",
                [""],
            )[0]
            or ""
        ).strip()

        message = str(
            parsed.get(
                "Body",
                [""],
            )[0]
            or ""
        ).strip()

        return sender, message

    except Exception:
        return "", ""


def _extract_twiml_message(
    body: bytes,
) -> str:
    try:
        text = body.decode(
            "utf-8",
            errors="replace",
        )
    except Exception:
        return ""

    match = re.search(
        r"<Message(?:\s[^>]*)?>(.*?)</Message>",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if not match:
        return ""

    message = match.group(1)

    message = (
        message
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )

    return message.strip()


class FeedbackEffectivenessMiddleware(
    BaseHTTPMiddleware,
):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        sender = ""
        user_message = ""

        is_whatsapp = (
            request.method.upper() == "POST"
            and request.url.path
            == "/webhook/whatsapp"
        )

        if is_whatsapp:
            try:
                request_body = await request.body()

                sender, user_message = (
                    _decode_whatsapp_form(
                        request_body,
                        request.headers.get(
                            "content-type",
                            "",
                        ),
                    )
                )

                if sender and user_message:
                    # Avalia exclusivamente a resposta anterior.
                    evaluate_incoming_feedback(
                        sender,
                        user_message,
                        current_subject="",
                    )

            except Exception:
                # O engine nunca pode bloquear o webhook.
                sender = ""
                user_message = ""

        response = await call_next(request)

        if not is_whatsapp or not sender:
            return response

        try:
            body_chunks = []

            async for chunk in response.body_iterator:
                body_chunks.append(chunk)

            response_body = b"".join(
                body_chunks
            )

            assistant_message = (
                _extract_twiml_message(
                    response_body
                )
            )

            if assistant_message:
                # Registra exclusivamente a resposta atual.
                register_outgoing_response(
                    sender,
                    assistant_message,
                    subject="",
                )

            headers = {
                key: value
                for key, value
                in response.headers.items()
                if key.lower()
                not in (
                    "content-length",
                    "transfer-encoding",
                )
            }

            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
                background=response.background,
            )

        except Exception:
            # A resposta original continua mesmo se o feedback falhar.
            return response
