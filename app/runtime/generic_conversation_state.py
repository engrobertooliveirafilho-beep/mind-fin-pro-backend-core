
from __future__ import annotations
import re, time, hashlib
from dataclasses import dataclass, field

@dataclass
class GenericConversationState:
    active_topic:str=""
    entities:list[str]=field(default_factory=list)
    intent:str=""
    stage:str="summary"
    substage:int=0
    depth:int=0
    mode:str="general"
    updated_at:float=0.0
    last_hashes:list[str]=field(default_factory=list)
    last_categories:list[str]=field(default_factory=list)

_STATE={}

DEEPEN_ALIASES=[
    "aprofundar","aprofunde","aprofunde ainda mais","detalhar",
    "mais detalhes","detalhe melhor","mais profundo","explique melhor",
    "continue","continue detalhando","vá mais fundo","va mais fundo"
]

ELDORA_SUBSTAGES=[
    ("architecture","Camada arquitetural: criar uma autoridade final que decide a resposta única antes do TwiML, recebendo tópico, intenção, memória e risco de fallback."),
    ("failure_modes","Falhas a eliminar: smalltalk indevido, troca de tópico, resposta duplicada, tom coach, vazamento técnico e loop de aprofundamento."),
    ("prioritization","Prioridade 80/20: estabilizar 15 mensagens reais no mesmo tópico antes de adicionar novas features."),
    ("execution","Execução: topic state genérico, SCA final, anti-loop semântico, score de UX e evidência por sessão."),
    ("validation","Validação: sequência humana com mudança de tópico, follow-up, aprofundamento e retorno ao tópico anterior sem bleed.")
]

FACTUAL_SUBSTAGES=[
    ("compatibility","Compatibilidade: confirmar aplicação direta, ano/modelo, peça exata, fonte e incerteza."),
    ("price","Preço: comparar loja, valor total, frete, disponibilidade, prazo e política de devolução."),
    ("alternatives","Alternativas: buscar usado, importado, paralelo e OEM sem trocar a peça por item parecido."),
    ("risk","Risco: evitar adaptação sem medir encaixe, estriado, geometria e retorno do pedal."),
    ("decision","Decisão: escolher só opção com compatibilidade explícita ou devolução segura.")
]

def _hash(t:str)->str:
    return hashlib.sha256((t or "").lower().strip().encode()).hexdigest()[:12]

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
    if any(x in msg for x in DEEPEN_ALIASES): return "deepen"
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

def _next_stage(prev:GenericConversationState|None,intent:str,topic_changed:bool)->tuple[str,int,int]:
    if not prev or topic_changed:
        return ("summary",0,0)
    stage,sub,depth=prev.stage,prev.substage,prev.depth
    if intent=="deepen":
        depth+=1
        if stage=="summary":
            stage="detail"
        sub+=1
        if sub>=5:
            sub=0
            order=["summary","detail","compare","decision","action","validation"]
            idx=min(order.index(stage)+1,len(order)-1) if stage in order else 1
            stage=order[idx]
    elif intent in ["economic_followup","factual_search","strategy_priority"]:
        depth+=1
    return (stage,sub,depth)

def update_conversation_state(sender_id:str,text:str)->GenericConversationState:
    key=sender_id or "default"
    prev=_STATE.get(key)
    intent=classify_intent(text)
    topic=infer_topic(text,prev)
    if not topic and prev:
        topic=prev.active_topic
    topic_changed=bool(prev and topic and topic!=prev.active_topic)

    ents=extract_entities(text)
    if prev and not ents and intent in ["deepen","economic_followup"]:
        ents=list(prev.entities)

    stage,sub,depth=_next_stage(prev,intent,topic_changed)
    mode="factual" if topic=="vehicle_parts_research" else "strategic" if topic=="eldora_runtime_ux" else "general"

    st=GenericConversationState(topic,ents,intent,stage,sub,depth,mode,time.time(),prev.last_hashes if prev else [],prev.last_categories if prev else [])
    _STATE[key]=st
    return st

def prevent_cross_topic(answer:str,state:GenericConversationState)->str:
    low=(answer or "").lower()
    if state.active_topic=="eldora_runtime_ux" and any(x in low for x in ["cr250","kick starter","pedal de partida","ims","red dragon"]):
        return "Aprofundando Eldora: o foco é fluidez real, autoridade de resposta única e continuidade por tópico sem fallback genérico."
    if state.active_topic=="vehicle_parts_research" and any(x in low for x in ["eldora","mind","neura"]):
        return "Mantendo o contexto da peça: vou responder só sobre compatibilidade, preço, adaptação e compra do item pesquisado."
    return answer

def _bank_answer(state:GenericConversationState)->tuple[str,str]:
    bank=ELDORA_SUBSTAGES if state.active_topic=="eldora_runtime_ux" else FACTUAL_SUBSTAGES
    idx=state.substage % len(bank)
    cat,text=bank[idx]
    prefix={
        "summary":"Resumo",
        "detail":"Detalhe",
        "compare":"Comparação",
        "decision":"Decisão",
        "action":"Ação",
        "validation":"Validação"
    }.get(state.stage,"Detalhe")
    if state.active_topic=="eldora_runtime_ux":
        text=f"Eldora / fluidez / autoridade: {text}"
    return cat, f"{prefix} / {cat}: {text}"

def progressive_answer(answer:str,state:GenericConversationState)->str:
    cleaned=(answer or "").replace("Digite APROFUNDAR para continuar","").replace("Se quiser, eu posso","").replace("😊","").strip()[:900]
    h=_hash(cleaned)
    repeated_hash=h in state.last_hashes

    cat,generated=_bank_answer(state)
    repeated_cat=cat in state.last_categories[-2:]

    generic=any(x in cleaned.lower() for x in [
        "não ficou claro","me dar um pouco mais de contexto","o que você gostaria",
        "tudo certo por aqui","como posso ajudar"
    ])

    if state.intent=="deepen" or repeated_hash or repeated_cat or generic:
        cleaned=generated

    state.last_hashes=(state.last_hashes+[h])[-8:]
    state.last_categories=(state.last_categories+[cat])[-4:]
    return prevent_cross_topic(cleaned,state)
