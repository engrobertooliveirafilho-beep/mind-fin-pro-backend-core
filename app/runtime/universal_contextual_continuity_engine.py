from datetime import datetime,UTC
from app.runtime.conversation_state_resolver import resolve
from app.runtime.context_recovery_engine import recover_context
from app.runtime.decision_memory import save_state

BANNED=[
"vamos seguir pelo ponto real",
"tudo certo por aqui",
"entendi",
"resposta direta",
"ação recomendada",
"memória contextual",
"como posso ajudar hoje"
]

SOCIAL_MAP = {
    "oi":"Oi.",
    "olá":"Oi.",
    "ola":"Oi.",
    "tudo bem":"Tudo bem por aqui. E com você?",
    "como vc está":"Estou funcionando bem. E você?",
    "como você está":"Estou funcionando bem. E você?",
    "quem é vc":"Sou a IA do MIND, focada em contexto e execução.",
    "quem é você":"Sou a IA do MIND, focada em contexto e execução.",
    "bom dia":"Bom dia.",
    "boa tarde":"Boa tarde.",
    "boa noite":"Boa noite."
}

def _social_reply(msg):
    m=(msg or "").lower().strip()
    for k,v in SOCIAL_MAP.items():
        if k in m:
            return v
    return "Oi."

def ucce_shadow_evaluate(sender_id,inbound_message,state=None):
    intent,s=resolve(sender_id,inbound_message)
    ctx=recover_context(s)
    msg=(inbound_message or "").strip().lower()

    if intent=="SOCIAL":
        reply=_social_reply(msg)

    elif intent=="FOLLOWUP":
        reply=(ctx["reply"] or
              f"Continuando sobre {ctx.get('topic') or 'isso'}: o último ponto foi {ctx.get('problem') or 'o teste anterior'}.")

    elif intent=="TROUBLESHOOTING":
        base=ctx.get("problem") or msg
        reply=f"O erro continua em: {base}. O que aconteceu no último teste?"

    elif intent=="TASK":
        reply=f"Vou focar nisso: {msg}."

    else:
        if ctx.get("open_loop") or ctx.get("topic") or ctx.get("task"):
            reply=(ctx.get("reply")
                   or f"Continuando sobre {ctx.get('topic') or 'o contexto anterior'}.")
        else:
            reply="O que você quer verificar?"

    for b in BANNED:
        reply=reply.replace(b,"")

    s["conversation_depth"]=s.get("conversation_depth",0)+1
    s["previous_intent"]=s.get("intent")
    s["intent"]=intent
    s["last_user_question"]=msg
    s["last_assistant_reply"]=reply
    s["last_meaningful_reply"]=reply
    s["updated_at"]=datetime.now(UTC).isoformat()

    save_state(sender_id,s)

    return {
        "classification":intent,
        "reply":reply,
        "confidence":0.93,
        "context_used":True,
        "state":s
    }
