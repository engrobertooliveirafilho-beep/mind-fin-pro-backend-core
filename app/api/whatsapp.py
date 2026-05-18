from fastapi import APIRouter, Request
from fastapi.responses import Response
from urllib.parse import parse_qs
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

router = APIRouter(prefix="/webhook", tags=["whatsapp"])

def twiml(message: str) -> str:
    safe = (message or "Eldora ativa.").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe}</Message></Response>'

def eldora_primary_runtime_reply(sender_id: str, inbound_text: str) -> str:
    try:
        result = run_cognitive_pipeline(user_id=sender_id or "whatsapp_user", message=inbound_text or "")
        return result.get("answer") or "Eldora ativa com pipeline cognitivo."
    except Exception as exc:
        return f"Eldora ativa em modo resiliente. Falha controlada: {str(exc)[:120]}"

@router.post("/whatsapp/cognitive")
async def whatsapp_webhook(request: Request):
    try:
        raw = (await request.body()).decode("utf-8", errors="ignore")
        data = parse_qs(raw)
        sender = data.get("From", ["whatsapp_user"])[0]
        body = data.get("Body", [""])[0]
        reply = eldora_primary_runtime_reply(sender, body)
    except Exception as exc:
        reply = f"Eldora ativa em fallback TwiML. Erro: {str(exc)[:120]}"
    return Response(content=twiml(reply), media_type="application/xml", status_code=200)

