from app.runtime.intent_arbitration_priority_engine import classify_intent
from app.runtime.p4_13g_router import route_natural_whatsapp
from app.runtime.ux_scoreboard import score_message

CASES = [
("Bom dia","SOCIAL"),
("Tudo bem?","SOCIAL"),
("Eu tô bem","SOCIAL"),
("Qual seu nome?","FACTUAL_QUESTION"),
("quero comprar uma moto k1300 quais são as melhores qualidades dela?","BUYING_ADVICE"),
("quais os pontos fortes da BMW K1300?","BUYING_ADVICE"),
("quanto é 5 / 4","FACTUAL_QUESTION"),
("9+5","CALCULATION"),
("e depois?","FOLLOWUP"),
("aprofunde","FOLLOWUP"),
]

def test_p4_13g_intent_priority():
    for text, expected in CASES:
        got = classify_intent(text)["intent"]
        if text == "quanto é 5 / 4":
            assert got in ("FACTUAL_QUESTION","CALCULATION")
        else:
            assert got == expected

def test_p4_13g_no_bad_fallbacks():
    for text, _ in CASES:
        ans = route_natural_whatsapp(text)
        s = score_message(text, ans)
        assert s["fallback"] == 0, (text, ans, s)
        assert s["leak"] == 0, (text, ans, s)
        assert s["chars"] <= 220
