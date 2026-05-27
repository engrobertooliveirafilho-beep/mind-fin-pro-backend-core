from typing import Dict, Any
from datetime import datetime

PROHIBITED_PHRASES = [
"Vamos seguir pelo ponto real",
"Tudo certo por aqui",
"Entendi. Continua",
"Vou aprofundar mantendo",
"Resposta direta:",
"Ação recomendada:",
"Memória contextual",
"Como posso ajudar hoje?"
]

def ucce_shadow_evaluate(sender_id:str,inbound_message:str,state:dict|None=None)->Dict[str,Any]:
    msg=(inbound_message or "").strip().lower()
    classification="AMBIGUOUS"
    reply="Pode explicar melhor em uma frase?"
    if any(x in msg for x in ["oi","ola","olá","bom dia","boa tarde","boa noite"]):
        classification="SOCIAL"; reply="Oi. O que você precisa?"
    elif any(x in msg for x in ["quanto é","quanto e","calcule"]):
        classification="CALCULATION"; reply="Preciso da expressão completa."
    elif any(x in msg for x in ["erro","deu errado","falhou","implantação","implantacao"]):
        classification="TROUBLESHOOTING"; reply="Qual foi o erro exato ou comportamento observado?"
    elif len(msg.split())<=3:
        classification="FOLLOWUP"; reply="Pode especificar o próximo ponto?"
    return {
        "classification":classification,
        "reply":reply,
        "confidence":0.65,
        "context_used":bool(state),
        "reasoning_trace":[],
        "scores":{},
        "state":{
            "sender_id":sender_id,
            "last_topic":None,
            "last_task":None,
            "last_reply":reply,
            "last_mode":classification,
            "last_intent":classification,
            "open_loop":False,
            "conversation_depth":1,
            "message_history_sample":[msg][-5:],
            "updated_at":datetime.utcnow().isoformat()
        }
    }
