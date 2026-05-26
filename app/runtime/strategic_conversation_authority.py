
from __future__ import annotations

_STATE={}

from app.runtime.global_topic_authority import global_topic_authority

def strategic_conversation_authority(answer:str,inbound:str="",sender_id:str="default")->str:
    msg=(inbound or "").lower()
    key=sender_id or "default"
    st=_STATE.get(key,{"topic":"","stage":0})

    if any(x in msg for x in ["eldora","mind","fluidez","ux","conversa","melhorar","lançamento","launch"]):
        st["topic"]="eldora_fluency"
        _STATE[key]=st

    active=st.get("topic")=="eldora_fluency"
    asks_priority=any(x in msg for x in ["primeiro","o que fazer","prioridade","por onde começar","fluidez","melhorar"])

    bad=any(x in (answer or "").lower() for x in [
        "tudo certo por aqui",
        "me dar um pouco mais de contexto",
        "o que você gostaria",
        "tem algum projeto em mente",
        "como posso ajudar"
    ])

    if active and (asks_priority or bad):
        st["stage"]=st.get("stage",0)+1
        _STATE[key]=st
        if "fluidez" in msg or st["stage"] <= 1:
            query=(user_message or "").lower()
    strategic_terms=("fluidez","prioridade","melhoria","melhorar","plano","estratégia","estrategia","roadmap","gargalo","otimização","otimizacao")
    if any(x in query for x in strategic_terms):
        return "Primeiro: melhorar a fluidez conversacional real, reduzir respostas genéricas, manter continuidade e validar comportamento real no WhatsApp."
    return None
        if "primeiro" in msg or "o que fazer" in msg:
            return "Faça primeiro o SCA real: uma autoridade final que decide a resposta única antes do TwiML. Depois vem memória, busca e refinamento."
        return "A próxima camada crítica é manter tópico ativo e impedir regressão para smalltalk. Sem isso, a Eldora parece instável."

    return global_topic_authority(answer, inbound, key)
