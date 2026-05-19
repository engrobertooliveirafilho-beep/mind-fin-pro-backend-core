from fastapi import APIRouter, Response, Form
from datetime import datetime, timezone
from pathlib import Path
import json

from app.api.whatsapp import eldora_primary_runtime_reply, twiml

router = APIRouter(prefix="/debug", tags=["debug"])

@router.post("/whatsapp-runtime-trace")
async def whatsapp_runtime_trace(
    From: str = Form(default="debug"),
    To: str = Form(default="debug"),
    Body: str = Form(default="")
):
    reply = eldora_primary_runtime_reply(From, Body)

    trace = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "from": From,
        "to": To,
        "body": Body,
        "reply": reply,
        "status": "TRACE_OK"
    }

    Path("whatsapp_runtime_trace_last.json").write_text(
        json.dumps(trace, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return Response(content=twiml(reply), media_type="application/xml")
