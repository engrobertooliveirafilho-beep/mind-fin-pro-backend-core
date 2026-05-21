
from __future__ import annotations

import re
from dataclasses import dataclass, field

@dataclass
class FactualSessionState:
    active_subject: str = ""
    active_item: str = ""
    active_brands: list[str] = field(default_factory=list)
    active_vehicle: str = ""
    last_intent: str = ""
    confidence: float = 0.0

def infer_factual_state(inbound: str, previous: FactualSessionState | None = None) -> FactualSessionState:
    msg=(inbound or "").lower()
    prev=previous or FactualSessionState()

    subject=prev.active_subject
    item=prev.active_item
    vehicle=prev.active_vehicle
    brands=list(prev.active_brands or [])
    intent=prev.last_intent
    confidence=prev.confidence

    if re.search(r"\b(cr\s?250r?|250r)\b", msg) or "2001" in msg or "2 tempos" in msg or "2t" in msg:
        subject="Honda CR250R 2001 2T"
        vehicle="Honda CR250R 2001 2 tempos"
        confidence=max(confidence,0.9)

    if any(x in msg for x in ["pedal","partida","kick","kickstart","kick starter"]):
        item="pedal de partida"
        confidence=max(confidence,0.9)

    if "ims" in msg and "IMS" not in brands:
        brands.append("IMS")
    if ("red dragon" in msg or "reddragon" in msg or "red-dragon" in msg) and "Red Dragon" not in brands:
        brands.append("Red Dragon")

    if any(x in msg for x in ["valor","preço","preco","custa","quanto","caro","barato","mais em conta"]):
        intent="price_search"
    elif any(x in msg for x in ["importar","importando","aliexpress","ebay","exterior"]):
        intent="import_search"
    elif any(x in msg for x in ["adapta","adaptar","outra moto","serve de outra"]):
        intent="adaptation_search"
    elif any(x in msg for x in ["verifique","verifica","verificar","quero que vc","quero que você","checar","confirmar","procure","pesquise","modelo correto","compatível","compativel","qual serve","paralelo"]):
        intent="compatibility_search"

    # Carry-over: follow-up econômico/técnico reaproveita contexto anterior.
    if not subject and prev.active_subject:
        subject=prev.active_subject
    if not item and prev.active_item:
        item=prev.active_item
    if not vehicle and prev.active_vehicle:
        vehicle=prev.active_vehicle
    if not brands and prev.active_brands:
        brands=list(prev.active_brands)

    if subject and item and intent:
        confidence=max(confidence,0.85)

    return FactualSessionState(subject,item,brands,vehicle,intent,confidence)

def should_factual_search(state: FactualSessionState) -> bool:
    return bool(state.confidence >= 0.75 and state.active_subject and state.active_item and state.last_intent)

def build_factual_prompt(state: FactualSessionState, inbound: str) -> str:
    brands=", ".join(state.active_brands) if state.active_brands else "IMS, Red Dragon e paralelos compatíveis"
    intent=state.last_intent or "compatibility_search"

    if intent=="price_search":
        task="preço atual, faixa de preço, lojas/fontes e alternativas mais baratas"
    elif intent=="import_search":
        task="opções de importação, riscos, preço estimado, frete/impostos prováveis e termos de busca em inglês"
    elif intent=="adaptation_search":
        task="se dá para adaptar de outra moto, quais riscos mecânicos, quais modelos evitar e quando só comprar compatível"
    else:
        task="compatibilidade, anos compatíveis, OEM/part number se souber, paralelos seguros e incertezas"

    return (
        "Pesquise na web e responda em português, curto, direto e factual. "
        f"Contexto ativo: {state.active_vehicle or state.active_subject}; peça: {state.active_item}; marcas: {brands}. "
        f"Tarefa: {task}. "
        "Não troque a peça por outro item. Não diga que não consegue procurar na web. "
        "Se não houver fonte suficiente, diga a incerteza claramente."
    )
