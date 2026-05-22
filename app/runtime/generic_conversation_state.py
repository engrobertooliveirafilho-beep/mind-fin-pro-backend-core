
from __future__ import annotations
import re, time, hashlib
from dataclasses import dataclass, field

@dataclass
class GenericConversationState:
    active_topic:str=""
    entities:list[str]=field(default_factory=list)
    intent:str=""
    stage:int=0
    mode:str="general"
    updated_at:float=0.0
    last_hashes:list[str]=field(default_factory=list)

_STATE={}
STAGES=["summary","detail","compare","decision","action"]

def _hash(t:str)->str:
    return hashlib.sha256((t or "").lower().strip().encode()).hexdigest()[:12]

def _tokens(text:str)->list[str]:
    return re.findall(r"[a-zA-ZÀ-ÿ0-9]{3,}", (text or "").lower())

def extract_entities(text:str)->list[str]:
    raw=(text or "").strip()
    ents=[]
    for pat in [
        r"\bCR\s?250R?\b", r"\b\d{4}\b", r"\bIMS\b", r"\bRed\s?Dragon\b",
        r"\bEldora\b", r"\bMIND\b", r"\bNEURA\b", r"\bWhatsApp\b",
        r"\bfluidez\b", r"\bpedal de partida\b"
    ]:
        for m in re.findall(pat, raw, flags=re.I):
            v=str(m).strip()
            if v and v not in ents:
                ents.append(v)
    return ents

def classify_intent(text:str)->str:
    msg=(text or "").lower()
    if any(x in msg for x in ["aprofundar","aprofunde","detalhar","mais detalhes"]): return "deepen"
    if any(x in msg for x in ["preço","preco","valor","custa","barato","caro","importar","importando"]): return "economic_followup"
    if any(x in msg for x in ["verifique","verifica","verificar","procure","pesquise","checar","confirmar"]): return "factual_search"
    if any(x in msg for x in ["o que fazer","primeiro","prioridade","melhorar","fluidez"]): return "strategy_priority"
    return "general"

def infer_topic(text:str, prev:GenericConversationState|None=None)->str:
    msg=(text or "").lower()
    if any(x in msg for x in ["eldora","mind","neura","fluidez","ux","runtime","whatsapp","lançamento","launch"]):
        return "eldora_runtime_ux"
    if any(x in msg for x in ["cr250","cr 250","250r","pedal","partida","ims","red dragon","moto"]):
        return "vehicle_parts_research"
    if prev and classify_intent(msg) in ["deepen","economic_followup"]:
        return prev.active_topic
    return ""

def update_conversation_state(sender_id:str,text:str)->GenericConversationState:
    key=sender_id or "default"
    prev=_STATE.get(key)
    intent=classify_intent(text)
    topic=infer_topic(text,prev)

    if not topic and prev:
        topic=prev.active_topic

    ents=extract_entities(text)
    if prev and not ents and intent in ["deepen","economic_followup"]:
        ents=list(prev.entities)

    stage=prev.stage if prev else 0
    if intent=="deepen":
        stage=min(stage+1,len(STAGES)-1)
    elif topic and (not prev or topic!=prev.active_topic):
        stage=0

    mode="factual" if topic=="vehicle_parts_research" else "strategic" if topic=="eldora_runtime_ux" else "general"

    st=GenericConversationState(topic,ents,intent,stage,mode,time.time(),prev.last_hashes if prev else [])
    _STATE[key]=st
    return st

def prevent_cross_topic(answer:str,state:GenericConversationState)->str:
    low=(answer or "").lower()
    if state.active_topic=="eldora_runtime_ux" and any(x in low for x in ["cr250","kick starter","pedal de partida","ims","red dragon"]):
        return "Aprofundando Eldora: o foco é fluidez real, autoridade de resposta única e continuidade por tópico sem fallback genérico."
    if state.active_topic=="vehicle_parts_research" and any(x in low for x in ["eldora","mind","neura"]):
        return "Mantendo o contexto da peça: vou responder só sobre compatibilidade, preço, adaptação e compra do item pesquisado."
    return answer

def progressive_answer(answer:str,state:GenericConversationState)->str:
    cleaned=(answer or "").replace("Digite APROFUNDAR para continuar","").replace("Se quiser, eu posso","").strip()[:900]
    h=_hash(cleaned)
    repeated=h in state.last_hashes
    stage=STAGES[state.stage]

    if repeated or state.intent=="deepen":
        if state.active_topic=="eldora_runtime_ux":
            bank={
                "detail":"Detalhe: primeiro estabilize a autoridade final de resposta. Ela deve escolher 1 resposta, cortar fallback genérico e preservar o tópico ativo.",
                "compare":"Comparação: o gargalo não é infra; é regressão de conversa. Sem tópico ativo, a Eldora parece instável mesmo com backend funcionando.",
                "decision":"Decisão: priorize SCA + topic state + anti-loop antes de novas features. Isso aumenta retenção e confiança.",
                "action":"Ação: validar 15 mensagens seguidas com mesmo tópico, sem smalltalk, sem troca de assunto e sem resposta duplicada."
            }
        else:
            bank={
                "detail":"Detalhe: aprofunde verificando compatibilidade, fonte, preço, disponibilidade e risco de adaptação.",
                "compare":"Comparação: prefira opção que cite explicitamente o modelo/ano alvo. Evite peça parecida sem confirmação de encaixe.",
                "decision":"Decisão: comprar só se anúncio/fonte citar compatibilidade direta ou permitir devolução.",
                "action":"Ação: comparar preço total, frete, prazo, política de troca e evidência de aplicação antes de comprar."
            }
        cleaned=bank.get(stage,cleaned)

    state.last_hashes=(state.last_hashes+[h])[-5:]
    return prevent_cross_topic(cleaned,state)
