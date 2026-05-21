
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field

STAGES=["summary","detail","compare","decision","action"]

@dataclass
class FactualConversationState:
    stage_index:int=0
    last_hashes:list[str]=field(default_factory=list)
    active_topic:str=""
    deepen_count:int=0

_STATE={}

def _hash(text:str)->str:
    return hashlib.sha256((text or "").strip().lower().encode()).hexdigest()[:12]

def _clean(text:str)->str:
    t=(text or "").strip()
    cuts=[
        "Digite APROFUNDAR para continuar.",
        "Digite APROFUNDAR para continuar",
        "Se quiser, eu posso",
        "se quiser, eu posso",
        "Estou aqui para ajudar",
        "😊"
    ]
    for c in cuts:
        t=t.replace(c,"").strip()
    return t[:900].strip()

def apply_factual_conversation_policy(answer:str,inbound:str="",sender_id:str="default")->str:
    msg=(inbound or "").lower()
    key=sender_id or "default"
    st=_STATE.get(key) or FactualConversationState()

    if any(x in msg for x in ["cr250","cr 250","250r","pedal","partida","ims","red dragon"]):
        st.active_topic="Honda CR250R 2001 2T / pedal de partida"

    if "aprofundar" in msg or "detalhar" in msg or "mais detalhes" in msg:
        st.deepen_count+=1
        st.stage_index=min(st.stage_index+1,len(STAGES)-1)

    stage=STAGES[st.stage_index]
    cleaned=_clean(answer)
    h=_hash(cleaned)

    if h in st.last_hashes:
        if stage=="detail":
            cleaned="Aprofundando: agora o ponto principal é separar oferta disponível de anúncio esgotado e confirmar se o anúncio cita CR250R 97/07."
        elif stage=="compare":
            cleaned="Comparação prática: IMS apareceu com preço real; Red Dragon não apareceu com preço confiável para CR250R 2001. Hoje eu priorizaria IMS com anúncio CR250R 97/07."
        elif stage=="decision":
            cleaned="Decisão objetiva: eu não compraria peça genérica de outra moto. Compraria só anúncio que cite CR250R 1997–2007 ou CR250R 2T."
        else:
            cleaned="Ação: procurar por 'kick starter Honda CR250R 1997 2007', 'CR250R 2001 kick start lever' e comparar preço + frete + prazo."

    st.last_hashes=(st.last_hashes+[h])[-5:]
    _STATE[key]=st
    return cleaned
