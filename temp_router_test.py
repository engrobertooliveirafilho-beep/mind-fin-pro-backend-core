from app.runtime.intent_arbitration_priority_engine import classify_intent
from app.runtime.p4_13g_router import route_natural_whatsapp

cases = [
"amos testar agora",
"vou viajar final de semana",
"me diga um ponto turistico em Holambra",
"qual seu nome?",
"tudo bem?",
"quero comprar uma moto k1300 quais são as melhores qualidades dela?",
"quais os pontos fortes da BMW K1300?",
"quanto é 5 / 4",
"9+5",
"e depois?",
"aprofunde",
]

for c in cases:
    print("\n" + "="*80)
    print("IN:", c)
    print("INTENT:", classify_intent(c))
    print("OUT:", route_natural_whatsapp(c))
