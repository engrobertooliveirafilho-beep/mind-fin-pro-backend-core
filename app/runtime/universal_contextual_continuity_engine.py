from datetime import datetime,UTC
from app.runtime.conversation_state_resolver import resolve
from app.runtime.context_recovery_engine import recover_context
from app.runtime.decision_memory import save_state
BANNED=["vamos seguir pelo ponto real","tudo certo por aqui","entendi","resposta direta","ação recomendada","memória contextual","como posso ajudar hoje"]
def ucce_shadow_evaluate(sender_id,inbound_message,state=None):
    intent,s=resolve(sender_id,inbound_message)
    ctx=recover_context(s)
    msg=(inbound_message or "").strip()
    if intent=="SOCIAL":
        reply="Oi. O que você precisa?"
    elif intent=="FOLLOWUP":
        reply=(ctx["reply"] or "Continuando: preciso do próximo resultado ou erro observado.")
    elif intent=="TROUBLESHOOTING":
        reply=f"O problema ainda é: {ctx['problem'] or msg}. Qual foi o último teste executado?"
        s["last_problem"]=msg
    elif intent=="TASK":
        reply=f"Vou focar nisso: {msg}."
        s["last_open_task"]=msg
    else:
        if ctx["open_loop"] or ctx["topic"] or ctx["task"]:
            reply=ctx["reply"] or "Continuando do contexto anterior."
        else:
            reply="O que exatamente você quer verificar?"
    for b in BANNED:
        if b.lower() in reply.lower():
            reply=reply.replace(b,"")
    s["conversation_depth"]=s.get("conversation_depth",0)+1
    s["previous_intent"]=s.get("intent")
    s["intent"]=intent
    s["last_user_question"]=msg
    s["last_assistant_reply"]=reply
    s["last_meaningful_reply"]=reply
    s["updated_at"]=datetime.now(UTC).isoformat()
    save_state(sender_id,s)
    return {"classification":intent,"reply":reply,"confidence":0.91,"context_used":True,"state":s}
