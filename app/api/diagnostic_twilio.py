
from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
from fastapi import APIRouter, Request, Response
from datetime import datetime, timezone
import json
from pathlib import Path

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])

@router.post("/twilio-inbound")
async def diagnostic_twilio_inbound(request: Request):
    form = await request.form()
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "headers": dict(request.headers),
        "form": dict(form),
        "status": "TWILIO_INBOUND_RECEIVED"
    }

    Path("diagnostic_twilio_last.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    body = str(form.get("Body", ""))

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
<Message>DIAG_OK recebido: {body}</Message>
</Response>"""

    return Response(content=xml, media_type="application/xml")


# FINAL_IDENTITY_BLOCK
def __identity_guard_last_hop(answer,user_message=""):
    return enforce_no_identity_in_normal_chat(user_message,answer)
