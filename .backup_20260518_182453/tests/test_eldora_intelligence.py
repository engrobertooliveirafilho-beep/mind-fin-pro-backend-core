from app.eldora.intelligence.orchestrator import normalize_input, classify_intent, respond

def test_normalize():
    assert normalize_input("  oi   mundo ") == "oi mundo"

def test_intent_study():
    assert classify_intent("quero estudar aula") == "study"

def test_lotofacil_safe():
    assert classify_intent("lotofácil") == "lotofacil_report"

def test_response_quality():
    out = respond({"text":"explique meu documento"})
    assert out["quality_gate"]["passed"] is True
    assert out["model"]["llm_real_declared"] in (True, False)
