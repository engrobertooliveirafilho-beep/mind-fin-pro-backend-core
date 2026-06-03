import re
import unicodedata
from dataclasses import dataclass, asdict

def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "").lower().strip())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s)

@dataclass
class SemanticDecision:
    intent: str
    domain: str
    confidence: float
    entities: dict
    answer: str

def extract_entities(t):
    entities = {}
    cities = ["holambra","campinas","jaguariuna","jaguariúna","sao paulo","são paulo"]
    brands = ["bmw","honda","yamaha","kawasaki","suzuki"]
    vehicles = re.findall(r"\b[a-z]{1,4}\d{2,5}[a-z]?\b", t)
    for c in cities:
        if norm(c) in t: entities["location"] = c
    for b in brands:
        if b in t: entities["brand"] = b.upper()
    if vehicles: entities["vehicle_model"] = vehicles[0].upper()
    return entities

def semantic_route(message, last_context=None):
    t = norm(message)
    ctx = last_context or {}
    ent = extract_entities(t)
    terms = set(t.split())

    if re.search(r"\d+\s*[\+\-\*/]\s*\d+", t) or any(x in t for x in ["quanto e", "calcule"]):
        expr = re.sub(r"[^0-9+\-*/(). ]", "", t.replace("quanto e","").replace("calcule",""))
        try:
            return SemanticDecision("CALCULATION","math",.99,ent,str(eval(expr,{"__builtins__":{}},{})))
        except Exception:
            return SemanticDecision("CLARIFY","math",.4,ent,"Me mande a conta completa.")

    if any(x in t for x in ["oi","bom dia","boa tarde","boa noite","tudo bem","estou bem","to bem","eldora"]):
        return SemanticDecision("SOCIAL","social",.9,ent,"")

    if any(x in t for x in ["comprar","vale a pena","moto","carro","veiculo","veículo"]) or ent.get("brand") or ent.get("vehicle_model"):
        model = " ".join(x for x in [ent.get("brand"), ent.get("vehicle_model")] if x) or "esse veículo"
        return SemanticDecision("ADVICE","vehicle_buying",.9,ent,f"{model} pode ser boa compra se histórico, manutenção, elétrica, suspensão e peças estiverem OK. Priorize laudo e teste frio.")

    if any(x in t for x in ["restaurante","comida","comer","almoço","jantar","bar","cafe","café"]):
        loc = ent.get("location") or ctx.get("location") or "a região"
        return SemanticDecision("RECOMMENDATION","local_food",.88,ent,f"Para comer em {loc}, eu filtraria por: avaliação recente, cozinha local, preço, estacionamento e distância. Peça 5 opções com faixa de preço.")

    if any(x in t for x in ["turistico","turístico","passeio","viagem","viajar","fim de semana","final de semana","roteiro"]):
        loc = ent.get("location") or ctx.get("location") or "o destino"
        return SemanticDecision("RECOMMENDATION","travel",.86,ent,f"Para {loc}, monte um roteiro simples: 1 ponto principal, 1 restaurante, tempo de deslocamento e plano B se chover.")

    if ctx and ctx.get("last_subject") and any(x in t for x in ["como","explique","explica","etapas","detalhe","detalhar","continue","continua","depois","qual","quais"]):
        return SemanticDecision("FOLLOWUP", ctx.get("last_domain","general"), .92, ent, "")

    if any(x in t for x in ["qual","quais","quem","onde","quando","como","me diga","cite","liste","melhores"]):
        return SemanticDecision("FACTUAL","general",.75,ent,"")

    if len(t.split()) <= 3:
        prev = ctx.get("domain")
        if prev == "local_food":
            loc = ctx.get("location","a região")
            return SemanticDecision("FOLLOWUP","local_food",.7,ent,f"Seguindo em comida em {loc}: melhor filtrar por tipo de cozinha, preço e distância.")
        return SemanticDecision("OPEN_LOOP","general",.55,ent,"")

    return SemanticDecision("OPEN_LOOP","general",.4,ent,"Entendi. Me diga o objetivo em uma frase.")

def route_semantic_whatsapp(message, last_context=None):
    return semantic_route(message,last_context).answer

