
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
    for c in ["Digite APROFUNDAR para continuar.","Digite APROFUNDAR para continuar","Se quiser, eu posso","se quiser, eu posso","Estou aqui para ajudar","😊"]:
        t=t.replace(c,"").strip()
    return t[:900].strip()

def apply_factual_conversation_policy(answer:str,inbound:str="",sender_id:str="default")->str:
    msg=(inbound or "").lower()
    key=sender_id or "default"
    st=_STATE.get(key) or FactualConversationState()

    deepen=any(x in msg for x in ["aprofundar","aprofunde","detalhar","mais detalhes"])
    if any(x in msg for x in ["cr250","cr 250","250r","pedal","partida","ims","red dragon"]) or deepen:
        st.active_topic = st.active_topic or "Honda CR250R 2001 2T / pedal de partida"

    if deepen:
        st.deepen_count += 1
        st.stage_index = min(st.stage_index+1, len(STAGES)-1)

    stage=STAGES[st.stage_index]
    cleaned=_clean(answer)
    h=_hash(cleaned)

    generic=("não ficou claro" in cleaned.lower() or "me dar um pouco mais de contexto" in cleaned.lower() or "que área específica" in cleaned.lower())

    if generic or h in st.last_hashes:
        if stage=="detail":
            cleaned="Aprofundando: o ponto crítico é confirmar anúncio que cite CR250R 1997–2007/2T, não peça parecida de CRF ou outra moto."
        elif stage=="compare":
            cleaned="Comparação prática: IMS teve preço real encontrado; Red Dragon não apareceu com fonte confiável para CR250R 2001. Hoje IMS é a rota mais segura."
        elif stage=="decision":
            cleaned="Decisão: eu compraria só se o anúncio citar CR250R 97/07 ou CR250R 2T. Evitaria adaptar pedal de CRF/YZ/KX sem medir encaixe."
        else:
            cleaned="Ação: buscar por 'Honda CR250R 1997 2007 kick starter', 'CR250R 2001 kick start lever' e comparar peça, frete, prazo e devolução."

    st.last_hashes=(st.last_hashes+[h])[-5:]
    _STATE[key]=st
    return cleaned
