from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def send(body, sender):
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    assert r.status_code in (200, 201)
    return r.text.lower()

def test_fitness_chain_context_locked():
    s = "+551199999901"
    a = send("quero emagrecer", s)
    b = send("monte um plano", s)
    c = send("quais", s)
    d = send("prossiga", s)
    joined = " ".join([a,b,c,d])
    assert "memória real do assunto" not in joined
    assert "moto elétrica" not in joined
    # O contrato deve validar continuidade sem exigir vocabulário exato
    # do provedor. Sinônimos semanticamente válidos são permitidos.
    semantic_markers = (
        "emagrecer",
        "aliment",
        "exerc",
        "peso",
        "treino",
        "cardio",
        "dieta",
    )
    assert any(marker in joined for marker in semantic_markers)

    from app.runtime.followup_unified_resolver import get_context

    context = get_context(s)
    assert context.get("active_subject") == "quero emagrecer"
    assert context.get("last_assistant_answer")
def test_humanization_does_not_enter_fitness():
    s = "+551199999902"
    a = send("quero humanizar você", s)
    b = send("quais são", s)
    assert "cardio" not in b
    assert "musculação" not in b
    assert "peso atual" not in b

def test_launch_does_not_enter_fitness():
    s = "+551199999903"
    a = send("quero lançar a Eldora", s)
    b = send("prossiga", s)
    assert "cardio" not in b
    assert "musculação" not in b
    assert "peso atual" not in b
