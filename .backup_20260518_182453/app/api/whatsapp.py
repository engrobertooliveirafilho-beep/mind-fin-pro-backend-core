from fastapi import APIRouter, Request
from fastapi.responses import Response
from urllib.parse import parse_qs
from app.runtime.cognitive_pipeline import run_cognitive_pipeline
from app.runtime.short_memory import remember, recall

router = APIRouter()

def twiml(message: str) -> str:
    safe = (message or "Eldora ativa.").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe}</Message></Response>'

def live_whatsapp_override(inbound_text: str) -> str | None:
    msg = (inbound_text or "").lower().strip()

    # normalização semântica leve
    msg = (
        msg.replace("á","a")
           .replace("à","a")
           .replace("ã","a")
           .replace("é","e")
           .replace("ê","e")
           .replace("í","i")
           .replace("ó","o")
           .replace("ô","o")
           .replace("õ","o")
           .replace("ú","u")
           .replace("?","")
           .replace("!","").replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","")
    )

    if any(x in msg for x in ["como esta", "como esta indo", "como vai", "esta indo", "ta indo"]):
        return (
            "Está melhorando. O runtime novo já responde no WhatsApp, "
            "mas ainda estamos refinando continuidade e naturalidade."
        )

    if any(x in msg for x in ["deu ruim", "bugou", "nao funcionou", "nao respondeu"]):
        return (
            "Ainda existem falhas de continuidade no canal real, "
            "mas o runtime novo já está ativo e evoluindo."
        )
    # =====================================================
    # SEMANTIC PLAN / NEXT STEP
    # =====================================================

    if any(x in msg for x in [
        "qual o plano",
        "como fazer",
        "e como fazer",
        "proximo passo",
        "próximo passo",
        "e agora",
        "qual caminho"
    ]):
        return (
            "O plano agora é estabilizar primeiro a conversa curta no WhatsApp, "
            "depois religar memória contextual e só então expandir a cognição completa."
        )
    if msg in ["como", "e como"]:
        return (
            "Fazendo em camadas: primeiro blindamos as respostas curtas do WhatsApp, "
            "depois conectamos memória contextual e por último liberamos a cognição profunda."
        )

    recent = recall("whatsapp_runtime")

    if any(x in msg for x in [
        "conseguiu",
        "parece que nao",
        "parece que não",
        "e depois",
        "mas porque",
        "mas por que"
    ]):

        if recent == "conversation_runtime":
            return (
                "Ainda não ficou totalmente natural. "
                "Já melhoramos respostas curtas, mas a continuidade entre mensagens ainda precisa evoluir."
            )

        if recent == "planning":
            return (
                "O plano já está funcionando parcialmente. "
                "Agora precisamos manter contexto entre perguntas curtas sem cair em resposta genérica."
            )
    # =====================================================
    # FUZZY SMALLTALK
    # =====================================================

    if any(x in msg for x in [
        "tudo be",
        "tudo bem",
        "como ta",
        "como esta"
    ]):
        remember("whatsapp_runtime","conversation_runtime")
        return (
            "Está melhorando. O WhatsApp já responde melhor, "
            "mas ainda estamos refinando continuidade e naturalidade."
        )

    # =====================================================
    # POSITIVE CONFIRMATION
    # =====================================================

    if any(x in msg for x in [
        "deu certo",
        "agora foi",
        "funcionou",
        "melhorou"
    ]):
        return (
            "Sim. Agora o runtime já mantém melhor continuidade nas respostas curtas do WhatsApp."
        )
    if any(x in msg for x in ["previsao do tempo", "previsão do tempo", "tempo para amanha", "tempo para amanhã", "clima amanha", "clima amanhã"]):
        return "Ainda não tenho consulta de clima real conectada no WhatsApp. O próximo passo é ligar uma API de previsão e responder com cidade, data, chuva e temperatura sem inventar."

    if any(x in msg for x in ["nao entendeu", "nao entnedeu", "não entendeu", "nao entendi", "não entendi"]):
        return "Entendi sim: você testou uma pergunta real e eu caí no fallback. Vamos corrigir adicionando handler específico e depois conectar consulta externa quando necessário."
    if msg in ["i", "oi", "olá", "ola"]:
        return "Oi, Roberto. Estou aqui. Vamos resolver isso direto."

    if any(x in msg for x in ["boa tarde", "bom dia", "boa noite"]):
        return "Boa tarde, Roberto. Estou aqui e acompanhando o contexto da conversa."

    if any(x in msg for x in ["como ta", "como tá", "tudo bem"]):
        return "Estou funcionando, mas ainda estamos ajustando o WhatsApp real para não cair em frase genérica."

    if any(x in msg for x in ["quem eh vc", "quem é vc", "quem é você"]):
        return "Eu sou a Eldora, a camada conversacional do MIND. Minha função é te ajudar sem você precisar reexplicar tudo."

    if any(x in msg for x in ["ainda nao conseguimos resolver", "ainda não conseguimos resolver", "nao esta funcionando", "não está funcionando", "não funciona"]):
        remember("whatsapp_runtime","conversation_runtime")
        return "Ainda não ficou bom no WhatsApp real. O problema agora é o handler do canal, não a cognição."

    if any(x in msg for x in [
        "agora ta funcionando",
        "agora está funcionando",
        "esta dando certo",
        "está dando certo",
        "como esta indo",
        "como está indo",
        "travou",
        "parou de falar"
    ]):
        return (
            "Está melhorando. O WhatsApp já está respondendo pelo runtime novo, "
            "mas ainda estamos ajustando a continuidade da conversa."
        )

    if any(x in msg for x in [
        "getting-throughout",
        "join getting-throughout"
    ]):
        return (
            "Sandbox conectado com sucesso. O canal do WhatsApp está ativo."
        )
    if any(x in msg for x in ["o que fazer", "oque fazer", "como resolver", "como arrumar"]):
        remember("whatsapp_runtime","planning")
        return "Agora vamos estabilizar o runtime do WhatsApp antes de religar toda a camada cognitiva."

    return None

def eldora_primary_runtime_reply(sender_id: str, inbound_text: str) -> str:
    override = live_whatsapp_override(inbound_text)

    msg = (inbound_text or "").lower().strip()

    if any(x in msg for x in ["nao entendi", "não entendi", "nao entnedeu"]):
        return (
            "Resumo simples: estamos ensinando o WhatsApp a não responder com frase genérica. "
            "Primeiro ele entende mensagens curtas; depois lembra o contexto; depois usa a cognição completa."
        )

    if any(x in msg for x in ["explique melhor", "detalhe melhor"]):
        return (
            "Na prática: criamos uma camada rápida antes da IA pesada. "
            "Essa camada segura saudações, dúvidas curtas, erros de digitação, reclamações e confirmações. "
            "Assim o usuário recebe resposta útil antes do pipeline profundo entrar."
        )

    if any(x in msg for x in ["aprofunde"]):
        return (
            "A arquitetura certa é: 1) shield semântico para conversa curta; "
            "2) memória transitória para continuidade; 3) roteador de intenção; "
            "4) cognição profunda do MIND; 5) auditoria de qualidade antes de responder."
        )

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










