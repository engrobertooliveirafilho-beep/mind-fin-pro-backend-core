from fastapi import APIRouter, Request
from fastapi.responses import Response
from urllib.parse import parse_qs
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

router = APIRouter()

def twiml(message: str) -> str:
    safe = (message or "Eldora ativa.").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe}</Message></Response>'

def live_whatsapp_override(inbound_text: str) -> str | None:
    msg = (inbound_text or "").lower().strip()

    if msg in ["i", "oi", "olá", "ola"]:
        return "Oi, Roberto. Estou aqui. Vamos resolver isso direto."

    if any(x in msg for x in ["boa tarde", "bom dia", "boa noite"]):
        return "Boa tarde, Roberto. Estou aqui e acompanhando o contexto da conversa."

    if any(x in msg for x in ["como ta", "como tá", "tudo bem"]):
        return "Estou funcionando, mas ainda estamos ajustando o WhatsApp real para não cair em frase genérica."

    if any(x in msg for x in ["quem eh vc", "quem é vc", "quem é você"]):
        return "Eu sou a Eldora, a camada conversacional do MIND. Minha função é te ajudar sem você precisar reexplicar tudo."

    if any(x in msg for x in ["ainda nao conseguimos resolver", "ainda não conseguimos resolver", "nao esta funcionando", "não está funcionando", "não funciona"]):
        return "Ainda não ficou bom no WhatsApp real. O problema agora é o handler do canal, não a cognição."

    if any(x in msg for x in ["o que fazer", "oque fazer", "como resolver", "como arrumar"]):
        return "Agora vamos estabilizar o runtime do WhatsApp antes de religar toda a camada cognitiva."

    return None

def eldora_primary_runtime_reply(sender_id: str, inbound_text: str) -> str:
    override = live_whatsapp_override(inbound_text)
    if override:
        return override

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
