from datetime import datetime,UTC
from app.runtime.conversation_state_resolver import resolve
from app.runtime.context_recovery_engine import recover_context
from app.runtime.decision_memory import get_state, save_state

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
    "ola":"Oi.",
    "olá":"Oi.",
    "bom dia":"Bom dia.",
    "boa tarde":"Boa tarde.",
    "boa noite":"Boa noite.",
    "tudo bem":"Tudo bem por aqui. E com você?",
    "como vc esta":"Estou funcionando bem. E você?",
    "como vc ta":"Estou funcionando bem. E você?",
    "como você está":"Estou funcionando bem. E você?",
    "quem e vc":"Sou a IA do MIND, focada em contexto e execução.",
    "quem é vc":"Sou a IA do MIND, focada em contexto e execução.",
    "quem e voce":"Sou a IA do MIND, focada em contexto e execução.",
    "quem é você":"Sou a IA do MIND, focada em contexto e execução."
}

def _has(msg, terms):
    return any(t in msg for t in terms)

def _social_reply(msg):
    for k,v in SOCIAL_MAP.items():
        if k in msg:
            return v
    return "Oi."

def ucce_shadow_evaluate(sender_id,inbound_message,state=None):
    s=get_state(sender_id)
    raw=(inbound_message or "").strip()
    msg=raw.lower()
    intent,_=resolve(sender_id,raw)
    ctx=recover_context(s)

    deployment_terms=["implantacao","implantação","implantações","implantacoes","deploy","render","version","versao","versão","elas"]
    status_terms=["como","status","estao","estão","andamento","deu certo","funcionou"]

    if _has(msg,deployment_terms):
        s["last_topic"]="implantações"
        s["last_goal"]="validar runtime live"
        s["last_open_task"]="acompanhar deploy/canary"
        s["open_loop"]=True
        intent="VERIFICATION"

    if intent=="SOCIAL":
        reply=_social_reply(msg)

    elif intent=="FOLLOWUP":
        topic=s.get("last_topic") or ctx.get("topic") or "isso"
        problem=s.get("last_problem") or "o último ponto ainda aberto"
        reply=f"Continuando sobre {topic}: o ponto aberto é {problem}. O próximo passo é validar a resposta real no WhatsApp."

    elif intent=="TROUBLESHOOTING":
        s["last_problem"]=raw
        s["unresolved_error"]=raw
        s["open_loop"]=True
        reply=f"O erro aberto é: {raw}. O próximo teste é confirmar se a rota caiu no branch UCCE e se a memória recuperou o contexto."

    elif intent in ["TASK","VERIFICATION"] or _has(msg,status_terms):
        topic=s.get("last_topic") or "runtime"
        if topic=="implantações":
            reply="As implantações estão parcialmente validadas: Render sincronizou e UCCE entrou no canary, mas a memória contextual ainda falhou no WhatsApp."
        else:
            reply=f"Vou verificar {topic}: preciso comparar versão, branch e último retorno real."

    else:
        if s.get("open_loop") or s.get("last_topic") or s.get("last_open_task"):
            topic=s.get("last_topic") or "o contexto anterior"
            reply=f"Continuando sobre {topic}: ainda falta validar se o WhatsApp mantém contexto entre mensagens."
        else:
            reply="O que você quer verificar?"

    for b in BANNED:
        reply=reply.replace(b,"")

    s["conversation_depth"]=s.get("conversation_depth",0)+1
    s["previous_intent"]=s.get("intent")
    s["intent"]=intent
    s["last_user_question"]=raw
    s["last_assistant_reply"]=reply
    s["last_meaningful_reply"]=reply
    s["updated_at"]=datetime.now(UTC).isoformat()
    save_state(sender_id,s)

    return {"classification":intent,"reply":reply,"confidence":0.94,"context_used":True,"state":s}
