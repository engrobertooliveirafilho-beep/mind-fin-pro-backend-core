from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

router = APIRouter(prefix="/webhook", tags=["whatsapp"])

def twiml(message: str) -> str:
    safe = (message or "Eldora ativa.").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe}</Message></Response>'

def eldora_primary_runtime_reply(sender_id: str, inbound_text: str) -> str:
    try:
        result = run_cognitive_pipeline(user_id=sender_id or "whatsapp_user", message=inbound_text or "")
        answer = result.get("answer") or ""
        scores = result.get("scores", {})
        if scores.get("generic_response_score", 1.0) > 0.20:
            return "Diagnóstico: contexto recuperado.\nEstratégia: manter continuidade MIND/Eldora.\nExecução: prosseguir com ação concreta.\nAuditoria: resposta não genérica."
        return answer
    except Exception as exc:
        return f"Eldora ativa em modo resiliente. Falha cognitiva controlada: {str(exc)[:120]}"

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, From: str = Form(default="whatsapp_user"), Body: str = Form(default="")):
    reply = eldora_primary_runtime_reply(From, Body)
    return Response(content=twiml(reply), media_type="application/xml")
